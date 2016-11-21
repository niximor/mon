from sqlalchemy import BigInteger
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import Enum
from sqlalchemy.orm import relationship

from api.db.base import Base
from api.db.entities.service import Service
from api.db.entities.service_status import ServiceStatus


class ServiceThreshold(Base):
    __tablename__ = "service_thresholds"

    id = Column(Integer, primary_key=True)
    probe_service_id = Column(Integer, ForeignKey(Service.id))
    service_status_id = Column(Integer, ForeignKey(ServiceStatus.id))
    reading = Column(String)
    min = Column(BigInteger, nullable=True)
    max = Column(BigInteger, nullable=True)
    source = Column(Enum("service", "configuration"))

    service_status = relationship("ServiceStatus", uselist=False)
