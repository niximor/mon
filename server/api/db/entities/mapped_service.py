from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.db.base import Base


class MappedService(Base):
    __tablename__ = "mapped_services"

    id = Column(Integer, primary_key=True)
    probe_service_id = Column(Integer, ForeignKey('probe_services.id'))
    name = Column(String)
    description = Column(String)
    status_id = Column(Integer, ForeignKey('status.id'))
    error_cause_id = Column(Integer, ForeignKey('error_cause.id'))

    # Current status is valid only for services which define thresholds. If no threshold is defined, the service
    # only collects data, and does not participate in warnings.
    current_status = Column(Integer, ForeignKey('service_status.id'), nullable=True)
    current_status_from = Column(DateTime, nullable=True)

    options = relationship("MappedServiceOption", passive_deletes=True, passive_updates=True)
    status = relationship("Status", uselist=False)
    error_cause = relationship("ErrorCause", uselist=False, innerjoin=False)
