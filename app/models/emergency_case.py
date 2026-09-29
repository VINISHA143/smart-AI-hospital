from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from app.database import Base


class EmergencyCase(Base):
    __tablename__ = "emergency_cases"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    assigned_doctor_id = Column(Integer)
    arrival_time = Column(TIMESTAMP)
    emergency_type = Column(String(100))
    symptoms = Column(Text)
    severity = Column(String(50), default="Medium")
    treatment_notes = Column(Text)
    status = Column(String(50), default="Active")
    discharge_time = Column(TIMESTAMP)