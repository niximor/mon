from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db.base import Base


class Service(Base):
    __tablename__ = "probe_services"

    id = Column(Integer, primary_key=True)
    probe_id = Column(Integer, ForeignKey("probes.id"))
    name = Column(String)
    description = Column(String)
    deleted = Column(Boolean)

    options = relationship("ServiceOption")
    thresholds = relationship("ServiceThreshold")
