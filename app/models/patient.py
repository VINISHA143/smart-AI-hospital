from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    phone = Column(String(20))
    email = Column(String(150))
    address = Column(Text)
    blood_group = Column(String(10))
    emergency_contact_name = Column(String(150))
    emergency_contact_phone = Column(String(20))
    created_at = Column(TIMESTAMP)