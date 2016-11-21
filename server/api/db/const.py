"""
Various database-related constants.
"""

from enum import Enum

from api.db.entities.error_cause import ErrorCause
from api.db.entities.service_status import ServiceStatus
from api.db.entities.status import Status
from config import config


class Const:
    """
    Access to system-wide constants loaded from DB.
    """
    def __init__(self):
        self._status = None
        self._errors = None
        self._service_status = None

    def load_status(self):
        """
        Load statuses from database.
        """
        session = config.session()
        try:
            statuses = session.query(Status).all()

            self._status = {}

            for status in statuses:
                self._status[status.id] = status.name
                self._status[status.name] = status.id
        finally:
            session.close()

    def load_errors(self):
        """
        Load error causes from database.
        """
        session = config.session()
        try:
            errors = session.query(ErrorCause).all()

            self._errors = {}

            for error in errors:
                self._errors[error.id] = error.name
                self._errors[error.name] = error.id
        finally:
            session.close()

    def load_service_status(self):
        """
        Load service statuses.
        """
        session = config.session()
        try:
            statuses = session.query(ServiceStatus).order_by(ServiceStatus.id).all()

            self._service_status = {}

            for status in statuses:
                self._service_status[status.id] = status.name
                self._service_status[status.name] = status.id

        finally:
            session.close()

    @property
    def status(self) -> dict:
        """
        Return status_id <-> status_name mapping.
        """
        if self._status is None:
            self.load_status()

        return self._status

    @property
    def error_cause(self) -> dict:
        """
        Return error_id <-> error_name mapping.
        """
        if self._errors is None:
            self.load_errors()

        return self._errors

    @property
    def service_status(self) -> dict:
        """
        Return service_status_id <-> service_status_name mapping.
        """
        if self._service_status is None:
            self.load_service_status()

        return self._service_status

const = Const()


class OptionDataType(Enum):
    """
    Enum of data types allowed for service options.
    """
    string = "string"
    int = "integer"
    double = "double"
    bool = "bool"
    list = "list"
