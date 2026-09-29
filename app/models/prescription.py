from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP
from app.database import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer, nullable=False)
    medical_record_id = Column(Integer)
    medicine_name = Column(String(150), nullable=False)
    dosage = Column(String(100))
    frequency = Column(String(100))
    duration = Column(String(100))
    instructions = Column(Text)
    prescribed_date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP)