from sqlalchemy import Column, Integer, String, Text, Date, Time, TIMESTAMP
from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer, nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(Time, nullable=False)
    reason = Column(Text)
    status = Column(String(50), default="Scheduled")
    notes = Column(Text)
    created_at = Column(TIMESTAMP)