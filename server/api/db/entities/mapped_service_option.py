from sqlalchemy import Column, ForeignKey, Integer, String

from api.db.base import Base
from api.db.entities.mapped_service import MappedService
from api.db.entities.service_option import ServiceOption


class MappedServiceOption(Base):
    __tablename__ = "mapped_service_options"

    id = Column(Integer, primary_key=True)
    mapped_service_id = Column(Integer, ForeignKey(MappedService.id))
    option_id = Column(Integer, ForeignKey(ServiceOption.id))
    value = Column(String)
