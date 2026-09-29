from sqlalchemy import Column, Integer, Text, Date, Time, TIMESTAMP, String
from app.database import Base


class Admission(Base):
    __tablename__ = "admissions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer)
    bed_id = Column(Integer)

    admission_date = Column(Date, nullable=False)
    admission_time = Column(Time)

    reason = Column(Text)
    diagnosis = Column(Text)

    status = Column(String(50), default="Admitted")

    discharge_date = Column(Date)
    discharge_notes = Column(Text)

    created_at = Column(TIMESTAMP)