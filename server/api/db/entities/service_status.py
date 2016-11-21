from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from api.db.base import Base


class ServiceStatus(Base):
    __tablename__ = "service_status"

    id = Column(Integer, primary_key=True)
    name = Column(String)
