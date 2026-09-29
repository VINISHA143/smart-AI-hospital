from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    action = Column(String(100), nullable=False)
    table_name = Column(String(100))
    record_id = Column(Integer)
    description = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(TIMESTAMP)