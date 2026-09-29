from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP
from app.database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    medicine_name = Column(String(150), nullable=False)
    category = Column(String(100))
    manufacturer = Column(String(150))
    batch_number = Column(String(100))
    quantity = Column(Integer, default=0)
    unit_price = Column(DECIMAL(10, 2), default=0.00)
    expiry_date = Column(Date)
    supplier_name = Column(String(150))
    created_at = Column(TIMESTAMP)