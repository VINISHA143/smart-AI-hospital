from sqlalchemy import Column, Integer, DECIMAL, String, Date, TIMESTAMP
from app.database import Base


class Billing(Base):
    __tablename__ = "billing"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, nullable=False)
    appointment_id = Column(Integer)
    bill_date = Column(Date, nullable=False)

    consultation_charge = Column(DECIMAL(10, 2), default=0.00)
    lab_charge = Column(DECIMAL(10, 2), default=0.00)
    medicine_charge = Column(DECIMAL(10, 2), default=0.00)
    room_charge = Column(DECIMAL(10, 2), default=0.00)
    other_charge = Column(DECIMAL(10, 2), default=0.00)

    total_amount = Column(DECIMAL(10, 2), default=0.00)

    payment_status = Column(
        String(50),
        default="Pending"
    )

    payment_method = Column(String(50))
    created_at = Column(TIMESTAMP)