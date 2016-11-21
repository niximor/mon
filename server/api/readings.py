"""
API for accessing and uploading probe readings.
"""
import logging
from fnmatch import fnmatch

from flask import request
from sqlalchemy.sql.functions import now

from api.db import Probe, MappedService, Service, const, ReadingValue, Reading, ServiceThreshold, ServiceStatusHistory
from config import config
from lib.schema import ExplicitObject, String, Integer, ExplicitArray
from lib.util import SafeResource, validate_input, validate_response


class Readings(SafeResource):
    """
    Stores and retrieves probe readings.
    """

    @validate_input(ExplicitArray(ExplicitObject({
        "service": Integer(title="Mapped service ID"),
        "reading": String(title="Value name"),
        "timestamp": String(format="date-time", title="Timestamp when the reading was taken."),
        "value": Integer(title="Value")
    })))
    @validate_response(ExplicitObject({"status": String(enum=["OK"])}, required=["status"]))
    def put(self, probe_name):
        """
        Put new reading to database.
        :param probe_name: Name of probe which sent the reading.
        """
        session = config.session()
        try:
            probe = session.query(Probe).filter(Probe.name == probe_name).one()

            # Load all active service IDs to be able to verify if posted service can be updated.
            active_service_ids = []
            active_services = {}

            for service in session.query(MappedService)\
                    .select_from(MappedService)\
                    .join(Service, MappedService.probe_service_id == Service.id)\
                    .filter(Service.probe_id == probe.id)\
                    .filter(MappedService.status_id == const.status["active"])\
                    .all():
                active_service_ids.append(service.id)
                active_services[service.id] = service

            readings_by_service = {}

            valid_service_ids = [value["service"] for value in request.json if value["service"] in active_service_ids]

            # Construct thresholds[mapping_id][reading_name] = [threshold1, threshold2, ...].
            thresholds_for_mapping = {}
            for threshold, mapped_service_id in session.query(ServiceThreshold, MappedService.id)\
                    .select_from(MappedService)\
                    .join(Service, Service.id == MappedService.probe_service_id)\
                    .join(ServiceThreshold, ServiceThreshold.probe_service_id == Service.id)\
                    .order_by(MappedService.id, ServiceThreshold.service_status_id)\
                    .filter(MappedService.id.in_(valid_service_ids)).all():
                thresholds_for_mapping\
                    .setdefault(mapped_service_id, {})\
                    .setdefault(threshold.reading, [])\
                    .append(threshold)

            for reading in session.query(Reading)\
                    .filter(Reading.mapped_service_id.in_(active_service_ids))\
                    .all():
                readings_by_service.setdefault(reading.mapped_service_id, {})[reading.name] = reading

            for value in request.json:
                if value["service"] not in active_service_ids:
                    logging.warning("Received reading for unknown service %s. Maybe it was removed or deactivated. "
                                    "Ignoring.")
                    continue

                # Test if reading value already exists
                db_reading = readings_by_service.setdefault(value["service"], {}).get(value["reading"])
                if db_reading is None:
                    db_reading = Reading(mapped_service_id=value["service"], name=value["reading"])
                    readings_by_service[value["service"]][value["reading"]] = db_reading
                    logging.debug("Create new reading %s." % (value["reading"], ))

                db_reading.values.append(ReadingValue(datetime=value["timestamp"], value=value["value"]))
                logging.debug("Store value %s=%s." % (db_reading.name, value["value"]))

                # TDetermine whether service changes status and write that to database.
                db_service = active_services[value["service"]]
                if value["service"] in thresholds_for_mapping:
                    # Determine what is current status of service.

                    thresholds = thresholds_for_mapping[value["service"]]

                    combined_thresholds = {}

                    # Determine possible keys and sort them by priority.
                    for reading, status_thresholds in thresholds.items():
                        if fnmatch(value["reading"], reading):
                            # Determine match priority. Be dummy here and think, that longer pattern is more accurate.
                            priority = len(reading)
                            for threshold in status_thresholds:
                                if threshold.service_status_id not in combined_thresholds or \
                                        combined_thresholds[threshold.service_status_id][0] < priority:
                                    combined_thresholds[threshold.service_status_id] = priority, threshold

                    # OK is default status.
                    current_status = const.service_status["ok"]
                    for key in sorted(combined_thresholds.keys()):
                        threshold = combined_thresholds[key][1]

                        if (threshold.min is not None and value["value"] < threshold.min) or (threshold.max is not None and value["value"] > threshold.max):
                            current_status = threshold.service_status_id

                    if db_service.current_status != current_status:
                        db_service.current_status = current_status
                        db_service.current_status_from = now()

                        # Create history entry.
                        session.add(ServiceStatusHistory(
                            mapped_service_id=db_service.id,
                            service_status_id=current_status,
                            timestamp=now()
                        ))
                        session.add(db_service)
                else:
                    if db_service.current_status is not None:
                        db_service.current_status = None
                        db_service.current_status_from = None

                        # Create history entry.
                        session.add(ServiceStatusHistory(
                            mapped_service_id=db_service.id,
                            service_status_id=None,
                            timestamp=now()
                        ))
                        session.add(db_service)

                session.add(db_reading)

            session.commit()

            return {"status": "OK"}
        except:
            session.rollback()
            raise
        finally:
            session.close()
