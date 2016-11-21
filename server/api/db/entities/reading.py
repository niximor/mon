from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db import MappedService
from api.db.base import Base


class Reading(Base):
    """
    One type of reading from mapped service.
    """
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True)
    mapped_service_id = Column(Integer, ForeignKey(MappedService.id))
    name = Column(String)

    values = relationship("ReadingValue")
