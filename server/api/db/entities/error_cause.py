from sqlalchemy import Column, Integer, String

from api.db.base import Base


class ErrorCause(Base):
    __tablename__ = "error_cause"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
