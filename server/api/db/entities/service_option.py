from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String

from api.db.base import Base
from api.db.entities.service import Service


class ServiceOption(Base):
    __tablename__ = "probe_service_options"

    id = Column(Integer, primary_key=True)
    identifier = Column(String)
    probe_service_id = Column(Integer, ForeignKey(Service.id))
    name = Column(String)
    data_type = Column(Enum("string", "integer", "double", "bool", "list"))
    required = Column(Boolean)
    description = Column(String)
