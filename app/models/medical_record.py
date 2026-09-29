from sqlalchemy import Column, Integer, Text, Date, TIMESTAMP
from app.database import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer, nullable=False)
    appointment_id = Column(Integer)

    visit_date = Column(Date, nullable=False)

    symptoms = Column(Text)
    diagnosis = Column(Text)
    treatment = Column(Text)
    doctor_notes = Column(Text)

    created_at = Column(TIMESTAMP)