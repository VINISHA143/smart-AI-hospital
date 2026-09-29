from sqlalchemy import Column, Integer, String, TIMESTAMP
from app.database import Base


class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    ward_name = Column(String(100), nullable=False)
    ward_type = Column(String(50))
    floor_number = Column(Integer)
    total_beds = Column(Integer, default=0)
    available_beds = Column(Integer, default=0)
    created_at = Column(TIMESTAMP)