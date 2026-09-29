from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP
from app.database import Base


class LabReport(Base):
    __tablename__ = "lab_reports"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    doctor_id = Column(Integer)
    test_name = Column(String(150), nullable=False)
    test_date = Column(Date, nullable=False)
    result_value = Column(String(100))
    unit = Column(String(50))
    reference_range = Column(String(100))
    report_status = Column(String(50), default="Completed")
    remarks = Column(Text)
    created_at = Column(TIMESTAMP)