"""
API for modifying service mappings.
"""

from flask import request, abort
from config import config
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from .db import select, Probe, Service, ServiceOption, MappedService, MappedServiceOption, Status, ErrorCause
from lib.util import SafeResource, validate_input, validate_response
from lib.schema import ExplicitArray, ExplicitObject, String, Object, OneOf, Boolean, Integer, Null
from werkzeug.exceptions import BadRequest
from .db import const

import logging


class Services(SafeResource):
    """
    Access set of mapped services for a probe.
    """

    SHOW_COLUMNS = {
        "id": MappedService.id,
        "name": MappedService.name,
        "description": MappedService.description,
        "service": Service.name.label("service"),
        "status": Status.name.label("status"),
        "error_cause": ErrorCause.description.label("error_cause"),
    }

    OPTIONS_COLUMNS = {
        "identifier": ServiceOption.identifier,
        "name": ServiceOption.name,
        "description": ServiceOption.description,
        "type": ServiceOption.data_type.label("type"),
        "required": ServiceOption.required
    }

    def __init__(self):
        super(Services, self).__init__()

    @validate_response(ExplicitArray(ExplicitObject({
        "id": Integer(),
        "name": String(),
        "description": String(),
        "service": String(),
        "status": String(),
        "error_cause": OneOf(String(), Null()),
        "options": ExplicitArray(ExplicitObject({
            "identifier": String(),
            "value": OneOf(String(), Null()),
            "name": String(),
            "description": String(),
            "type": String(),
            "required": Boolean(),
        }))
    })))
    def get(self, probe_name):
        """
        List mapped services of probe.
        :param probe_name: Probe name
        """
        session = config.session()

        try:
            probe = session.query(Probe).filter_by(name=probe_name).one()

            allowed_statuses = []
            for status in request.args.getlist("status"):
                if status == "all":
                    allowed_statuses = None
                    break

                if status in const.status.keys():
                    allowed_statuses.append(const.status[status])
                else:
                    raise BadRequest("Bad status value: '%s'. Must be one of %s."
                                     % (status, ",".join(const.status.keys())))

            if not allowed_statuses and allowed_statuses is not None:
                allowed_statuses.append(const.status["active"])

            show = request.args.getlist("show")

            show_options = []

            for column in show:
                if column.startswith("options."):
                    show_options.append(column[len("options."):])

            for column in show_options:
                show.remove("options.%s" % (column, ))

            mapped_services = select(session, show, self.SHOW_COLUMNS)\
                .select_from(MappedService)\
                .add_column(MappedService.id.label("id"))\
                .add_column(MappedService.probe_service_id.label("probe_service_id"))\
                .join(Service, MappedService.probe_service_id == Service.id)\
                .join(Status, MappedService.status_id == Status.id)\
                .outerjoin(ErrorCause, MappedService.error_cause_id == ErrorCause.id)\
                .filter((Service.probe_id == probe.id))\
                .order_by(MappedService.name)

            if allowed_statuses:
                mapped_services = mapped_services.filter(MappedService.status_id.in_(allowed_statuses))

            ids = request.args.getlist("id")
            if ids:
                mapped_services = mapped_services.filter(MappedService.id.in_(ids))

            services = []
            service_ids = set()
            mapped_ids = set()

            for row in mapped_services.all():
                service = row._asdict()
                services.append(service)
                service_ids.add(service["probe_service_id"])
                mapped_ids.add(service["id"])

            if show_options:
                load_value = False

                if "value" in show_options:
                    load_value = True
                    show_options.remove("value")

                # Select all options for given services
                options = select(session, show_options, self.OPTIONS_COLUMNS)\
                    .add_column(ServiceOption.probe_service_id)\
                    .add_column(ServiceOption.id)\
                    .filter(ServiceOption.probe_service_id.in_(service_ids))

                options_for_service = {}

                for row in options.all():
                    option = row._asdict()
                    options_for_service.setdefault(option["probe_service_id"], []).append(option)

                values_by_mapping = {}

                if load_value:
                    for row in session.query(MappedServiceOption.value, MappedServiceOption.mapped_service_id, MappedServiceOption.option_id)\
                            .filter(MappedServiceOption.mapped_service_id.in_(mapped_ids)).all():
                        value = row._asdict()

                        values_by_mapping.setdefault(value["mapped_service_id"], {})[value["option_id"]] = value["value"]

                for service in services:
                    options = [option.copy() for option in options_for_service.get(service["probe_service_id"], [])]

                    if load_value:
                        for option in options:
                            option["value"] = values_by_mapping.get(service["id"], {}).get(option["id"])

                    for option in options:
                        del option["probe_service_id"], option["id"]

                    service["options"] = options

            # Clean up the result struct from internal items.
            for service in services:
                del service["probe_service_id"]
                if "id" not in show:
                    del service["id"]

            return services
        finally:
            session.commit()

    @validate_input(ExplicitArray(ExplicitObject({
        "name": String(),
        "description": String(),
        "service": String(),
        "options": Object(additional_properties=String())
    }, required=["name", "service"])))
    @validate_response(ExplicitObject({"status": String(enum=["OK"])}, required=["status"]))
    def put(self, probe_name):
        """
        Create new service mapping.
        :param probe_name: Name of probe.
        """
        data = request.json

        # List service IDs to load.
        services_to_load = [mapping["service"] for mapping in data]

        session = config.session()

        try:
            probe = session.query(Probe).filter_by(name=probe_name).one()
            services = {
                service.name: service
                for service in session.query(Service).options(joinedload("options")).filter(and_(
                    Service.name.in_(services_to_load),
                    Service.probe_id == probe.id
                )).all()
            }

            services_by_id = {}
            for service in services.values():
                services_by_id[service.id] = service

            if len(services) != len(services_to_load):
                abort(404)

            mappings = []

            for mapping in data:
                service = services[mapping["service"]]

                db_mapping = MappedService(
                    probe_service_id=service.id,
                    name=mapping["name"],
                    description=mapping.get("description", ""),
                    status_id=const.status["active"],
                )
                db_mapping.options = []

                required_set = True

                for option in service.options:
                    option_value = mapping.get("options", {}).get(option.identifier, "")

                    if option_value == "":
                        if option.required:
                            required_set = False
                        continue

                    # Test data types
                    try:
                        if option.data_type == "string":
                            pass
                        elif option.data_type == "integer":
                            option_value = str(int(option_value))
                        elif option.data_type == "double":
                            option_value = str(float(option_value))
                        elif option.data_type == "bool":
                            option_value = "1" if bool(option_value) else "0"
                        elif option.data_type == "list":
                            option_value = "\n".join([
                                                         value
                                                         for value in option_value.split("\n")
                                                         if value.strip() != ""
                                                     ])
                        else:
                            raise ValueError()
                    except ValueError:
                        abort(400)

                    db_mapping.options.append(MappedServiceOption(
                        option_id=option.id,
                        value=option_value
                    ))
                    mappings.append(db_mapping)

                if not required_set:
                    db_mapping.status_id = const.status["error"]
                    db_mapping.error_cause_id = const.error_cause["ERROR_MISSING_REQUIRED_OPTION"]

            session.add_all(mappings)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return {"status": "OK"}

    @validate_input(ExplicitArray(ExplicitObject({
        "id": Integer(),
        "name": String(),
        "description": String(),
        "status": String(enum=["active", "suspended"]),
        "options": Object(additional_properties=String())
    }, required=["id"])))
    @validate_response(ExplicitObject({"status": String(enum=["OK"])}, required=["status"]))
    def patch(self, probe_name):
        """
        Update mapping options.
        """
        session = config.session()

        try:
            probe = session.query(Probe).filter(Probe.name == probe_name).one()

            services = session.query(MappedService, Service)\
                .join(Service, MappedService.probe_service_id == Service.id)\
                .filter(MappedService.id.in_([service["id"] for service in request.json]))\
                .filter(Service.probe_id == probe.id)\
                .all()

            if len(services) != len(request.json):
                abort(404)

            services_by_id = {
                mapping_service[0].id: mapping_service
                for mapping_service in services
            }

            # Modify service
            for service in request.json:
                db_mapping, db_service = services_by_id[int(service["id"])]

                if "name" in service:
                    db_mapping.name = service["name"]

                if "description" in service:
                    db_mapping.description = service["description"]

                # Modify status, but only if it is not error.
                if "status" in service and db_mapping.status_id != const.status["error"]:
                    db_mapping.status_id = const.status[service["status"]]

                options_by_identifier = {}

                for option in db_service.options:
                    options_by_identifier[option.identifier] = option

                mapped_options_by_option_id = {}
                for option in db_mapping.options:
                    mapped_options_by_option_id[option.option_id] = option

                if "options" in service:
                    found_options = []
                    required_filled = True

                    for option_identifier, option_value in service["options"].items():
                        option = options_by_identifier[option_identifier]

                        # Empty options are not allowed.
                        if option_value == "":
                            if option.required:
                                required_filled = False

                            continue

                        # Test data types
                        try:
                            if option.data_type == "string":
                                pass
                            elif option.data_type == "integer":
                                option_value = str(int(option_value))
                            elif option.data_type == "double":
                                option_value = str(float(option_value))
                            elif option.data_type == "bool":
                                option_value = "1" if bool(option_value) else "0"
                            elif option.data_type == "list":
                                option_value = "\n".join(
                                    [value for value in option_value.split("\n") if value.strip() != ""])
                            else:
                                raise ValueError()
                        except ValueError:
                            abort(400)

                        found_options.append(option.id)

                        if option.id in mapped_options_by_option_id:
                            mapped_options_by_option_id[option.id].value = option_value

                        else:
                            mapping_option = MappedServiceOption(option_id=option.id, value=option_value)
                            db_mapping.options.append(mapping_option)

                    for option_id, option in mapped_options_by_option_id.items():
                        if option_id not in found_options:
                            session.delete(option)

                    # If all required options are filled and service is in error state because of this, reactivate the
                    # service.
                    if required_filled \
                            and db_mapping.status_id == const.status["error"] \
                            and db_mapping.error_cause_id == const.error_cause["ERROR_MISSING_REQUIRED_OPTION"]:
                        db_mapping.status_id = const.status["active"]
                        db_mapping.error_cause_id = None

                session.add(db_mapping)

            session.commit()

            return {"status": "OK"}
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @validate_response(ExplicitObject({"status": String(enum=["OK"])}, required=["status"]))
    def delete(self, probe_name):
        """
        Delete mapped services from probe.
        """
        session = config.session()

        try:
            probe = session.query(Probe).filter(Probe.name == probe_name).one()

            logging.info("Deleting service mapping where id in %s" % ",".join(request.args.getlist("id")))
            for service in session.query(MappedService)\
                    .join(Service, Service.id == MappedService.probe_service_id)\
                    .filter(MappedService.id.in_(request.args.getlist("id")))\
                    .filter(Service.probe_id == probe.id).all():

                session.delete(service)

            session.commit()

            return {"status": "OK"}
        except:
            session.rollback()
            raise

        finally:
            session.close()
