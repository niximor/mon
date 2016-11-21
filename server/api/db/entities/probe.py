from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from api.db.base import Base
from api.db.entities.service import Service


class Probe(Base):
    __tablename__ = "probes"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    services = relationship(Service)
    mappings = relationship("MappedService", secondary=Service.__table__)
