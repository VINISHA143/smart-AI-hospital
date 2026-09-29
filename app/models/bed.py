from sqlalchemy import Column, Integer, String, Date, TIMESTAMP
from app.database import Base


class Bed(Base):
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, nullable=False)
    bed_number = Column(String(50), nullable=False)
    bed_type = Column(String(50))
    status = Column(String(50), default="Available")
    patient_id = Column(Integer)
    admission_date = Column(Date)
    discharge_date = Column(Date)
    created_at = Column(TIMESTAMP)