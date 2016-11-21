from sqlalchemy import BigInteger, Column, DateTime, ForeignKey,Integer

from api.db.base import Base
from api.db.entities.reading import Reading


class ReadingValue(Base):
    """
    One value of reading.
    """
    __tablename__ = "reading_values"

    id = Column(BigInteger, primary_key=True)
    reading = Column(Integer, ForeignKey(Reading.id))
    datetime = Column(DateTime)
    value = Column(BigInteger)
