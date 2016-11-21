from flask import request
from config import config
from lib.util import SafeResource, validate_input, validate_response
from lib.schema import ExplicitObject, ExplicitArray, String, Boolean, Integer, Object, Null, OneOf

import sqlalchemy
import logging

import api.db as entity
from api.db import select, const, OptionDataType


class Probe(SafeResource):
    """
    One specific probe.
    """

    @validate_response(ExplicitObject({
        "name": String(),
        "services": ExplicitArray(ExplicitObject({
            "name": String(),
            "description": String(),
            "deleted": Boolean(),
            "options": ExplicitArray(ExplicitObject({
                "identifier": String(),
                "name": String(),
                "type": String(enum=[
                    data_type.value
                    for data_type in OptionDataType
                ]),
                "description": String(),
                "required": Boolean()
            }))
        }))
    }))
    def get(self, name):
        """
        Return probe configuration.
        """
        session = config.session()
        try:
            probe = session.query(entity.Probe).filter_by(name=name).one()
            return {
                "name": probe.name,
                "services": [{
                    "name": service.name,
                    "description": service.description,
                    "deleted": service.deleted,
                    "options": [{
                        "identifier": option.identifier,
                        "name": option.name,
                        "type": option.data_type,
                        "description": option.description,
                        "required": option.required
                    } for option in service.options]
                } for service in probe.services]
            }
        finally:
            session.commit()


class Probes(SafeResource):
    """
    Set of probes.
    """

    SELECT_COLUMN_MAPPING = {
        "name": entity.Probe.name,
        "warnings": sqlalchemy.sql.expression.bindparam("warnings", 0),
        "errors": sqlalchemy.sql.expression.bindparam("errors", 0),
        "num_services": sqlalchemy.func.count(sqlalchemy.distinct(entity.Service.id)).label("num_services"),
        "num_mapped": sqlalchemy.func.count(sqlalchemy.distinct(entity.MappedService.id)).label("num_mapped")
    }

    TABLE_JOINS = {
        "service": (entity.Service, entity.Service.probe_id == entity.Probe.id),
        "mapped_service": (entity.MappedService, entity.MappedService.probe_service_id == entity.Service.id)
    }

    SELECT_JOIN_MAPPING = {
        "num_services": ("service", ),
        "num_mapped": ("service", "mapped_service", ),
    }

    @validate_response(ExplicitArray(items=ExplicitObject(properties={
        "name": String(),
        "warnings": Integer(),
        "errors": Integer(),
        "num_services": Integer(),
        "num_mapped": Integer()
    })))
    def get(self):
        """
        List of probes.
        """
        session = config.session()
        try:
            query = select(session, request.args.getlist("show"), self.SELECT_COLUMN_MAPPING, self.SELECT_JOIN_MAPPING,
                           self.TABLE_JOINS).order_by(entity.Probe.name)

            result = [probe._asdict() for probe in query.all()]
            logging.info(result)
            return result
        finally:
            session.commit()

    @validate_input(ExplicitObject({
        "name": String(),
        "services": ExplicitArray(ExplicitObject({
            "name": String(),
            "description": String(),
            "thresholds": Object(additional_properties=ExplicitObject(
                {
                    "status": String(enum=[
                        status
                        for status in const.service_status.keys()
                        if isinstance(status, str)
                    ]),
                    "min": OneOf(Null(), Integer()),
                    "max": OneOf(Null(), Integer())
                },
                required=["status", "min", "max"],
                title="Thresholds for various service states.",
                description="The specified min-max interval is the range, where this state is NOT valid. If you for "
                            "example specify status=warning, min=0, max=10, then anything that is <0 and >10 will "
                            "issue a warning.\n"
                            "The key in this object is name of reading or '*' for all readings."
            )),
            "options": ExplicitArray(ExplicitObject({
                "name": String(min_length=1),
                "identifier": String(pattern="^[a-zA-Z_][a-zA-Z0-9_.-]*$"),
                "type": String(enum=[data_type.value for data_type in OptionDataType], default="string"),
                "description": String(),
                "required": Boolean(default=False),
            }, required=["identifier"]))
        }, required=["name"]))
    }, required=["name", "services"]))
    @validate_response(ExplicitObject({
        "status": String(enum=["OK"])
    }, required=["status"]))
    def put(self):
        """
        Create/update probe data.
        """
        data = request.json

        session = config.session()
        try:
            probe = session.query(entity.Probe).filter_by(name=data["name"]).one()

            services_by_name = {}

            for service in probe.services:
                services_by_name[service.name] = service

            reported_services_names = []

            for service in data.get("services", []):
                if service["name"] not in services_by_name:
                    db_service = entity.Service(name=service["name"], description=service.get("description", ""))
                    probe.services.append(db_service)
                    services_by_name[db_service.name] = db_service
                else:
                    db_service = services_by_name[service["name"]]
                    db_service.description = service.get("description", "")
                    db_service.deleted = False

                reported_services_names.append(service["name"])

                options_by_identifier = {}
                reported_option_identifiers = []

                for option in db_service.options:
                    options_by_identifier[option.identifier] = option

                required_options = []
                new_required_option = False

                for option in service.get("options", []):
                    reported_option_identifiers.append(option["identifier"])
                    if option["identifier"] not in options_by_identifier:
                        db_option = entity.ServiceOption(identifier=option["identifier"],
                                                         name=option.get("name", option["identifier"]),
                                                         description=option.get("description", ""),
                                                         data_type=option.get("type", "string"),
                                                         required=option.get("required", False))
                        db_service.options.append(db_option)

                        # Set all mapped services nonfunctional if new required option is introduced.
                        if db_option.required and db_service.id:
                            new_required_option = True
                    else:
                        db_option = options_by_identifier[option["identifier"]]
                        db_option.name = option.get("name", option["identifier"])
                        db_option.description = option.get("description", "")
                        db_option.data_type = option.get("type", "string")
                        db_option.required = option.get("required", False)

                        if db_option.required and db_service.id:
                            required_options.append(db_option.id)

                # Set service error if there is new required option. First case is when there is whole new option,
                # second is for situations, when option becomes required.
                if new_required_option or db_service.deleted:
                    session.execute("""UPDATE mapped_services
                                    SET status_id = :status_id, error_cause_id = :error_cause_id
                                    WHERE probe_service_id = :service_id""",
                                    {
                                        "status_id": const.status["error"],
                                        "error_cause_id": (const.error_cause["ERROR_MISSING_REQUIRED_OPTION"]
                                                           if new_required_option
                                                           else const.error_cause["ERROR_SERVICE_UNAVAILABLE"]),
                                        "service_id": db_service.id
                                    })
                elif required_options:
                    session.execute("""UPDATE mapped_services m
                                    LEFT JOIN mapped_service_options o
                                        ON (o.mapped_service_id = m.id AND o.option_id IN (""" + ",".join(map(str, required_options)) + """))
                                    SET m.status_id = :status_id, m.error_cause_id = :error_cause_id
                                    WHERE o.id IS NULL""",
                                    {
                                        "status_id": const.status["error"],
                                        "error_cause_id": const.error_cause["ERROR_MISSING_REQUIRED_OPTION"],
                                        "service_id": db_service.id
                                    })

                # Delete no longer known options.
                for option_identifier, option in options_by_identifier.items():
                    if option_identifier not in reported_option_identifiers:
                        session.delete(option)

                # Update / create thresholds.
                known_thresholds = []
                for threshold in db_service.thresholds:
                    known_thresholds.append(threshold)

                for name, limits in service.get("thresholds", {}).items():
                    found = False
                    for db_threshold in known_thresholds:
                        if db_threshold.reading == name and \
                                const.service_status[db_threshold.service_status_id] == limits["status"]:
                            found = True

                            # Update only if the limits come from service and are not overwritten by the configuration.
                            if db_threshold.source == "service":
                                db_threshold.min = limits.get("min", None)
                                db_threshold.max = limits.get("max", None)
                            break

                    if not found:
                        db_service.thresholds.append(entity.ServiceThreshold(
                            service_status_id=const.service_status[limits["status"]],
                            reading=name,
                            min=limits.get("min", None),
                            max=limits.get("max", None),
                            source="service"
                        ))

            # Delete no longer known services
            for service_name, service in services_by_name.items():
                if service_name not in reported_services_names:
                    service.deleted = True

            session.add(probe)
        except Exception:
            session.rollback()
            raise
        finally:
            session.commit()

        return {"status": "OK"}
