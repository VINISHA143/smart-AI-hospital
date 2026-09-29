from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, TIMESTAMP
from app.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)
    phone = Column(String(20))
    email = Column(String(150))
    license_number = Column(String(100), unique=True)
    experience_years = Column(Integer, default=0)
    consultation_fee = Column(DECIMAL(10, 2), default=0.00)
    availability_status = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP)