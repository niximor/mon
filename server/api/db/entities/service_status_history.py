from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer

from api.db.base import Base


class ServiceStatusHistory(Base):
    __tablename__ = "service_status_history"

    id = Column(Integer, primary_key=True)
    mapped_service_id = Column(Integer, ForeignKey("mapped_services.id"))
    service_status_id = Column(Integer, ForeignKey("service_status.id"))
    timestamp = Column(DateTime)
