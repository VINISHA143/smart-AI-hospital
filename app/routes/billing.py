from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from datetime import date

from app.database import SessionLocal
from app.models.billing import Billing
from app.auth import require_permission


router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)


# =========================
# DATABASE
# =========================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================
# SCHEMA
# =========================

class BillingCreate(BaseModel):
    patient_id: int
    appointment_id: int | None = None

    bill_date: date

    consultation_fee: float = Field(
        default=0.0,
        ge=0
    )

    lab_charges: float = Field(
        default=0.0,
        ge=0
    )

    medicine_charges: float = Field(
        default=0.0,
        ge=0
    )

    other_charges: float = Field(
        default=0.0,
        ge=0
    )

    total_amount: float = Field(
        default=0.0,
        ge=0
    )

    payment_status: str = "Pending"
    payment_method: str | None = None


# =========================
# GET ALL BILLING RECORDS
# =========================

@router.get("/")
def get_bills(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("billing")
    )
):
    return db.query(Billing).all()


# =========================
# GET BILLING BY ID
# =========================

@router.get("/{bill_id}")
def get_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("billing")
    )
):
    bill = (
        db.query(Billing)
        .filter(Billing.id == bill_id)
        .first()
    )

    if not bill:
        raise HTTPException(
            status_code=404,
            detail="Billing record not found"
        )

    return bill


# =========================
# CREATE BILLING RECORD
# =========================

@router.post("/")
def create_bill(
    bill: BillingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("billing")
    )
):
    new_bill = Billing(
        patient_id=bill.patient_id,
        appointment_id=bill.appointment_id,
        bill_date=bill.bill_date,
        consultation_fee=bill.consultation_fee,
        lab_charges=bill.lab_charges,
        medicine_charges=bill.medicine_charges,
        other_charges=bill.other_charges,
        total_amount=bill.total_amount,
        payment_status=bill.payment_status,
        payment_method=bill.payment_method
    )

    try:
        db.add(new_bill)
        db.commit()
        db.refresh(new_bill)

        return new_bill

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Billing record could not be created because of a database conflict"
        )


# =========================
# UPDATE BILLING RECORD
# =========================

@router.put("/{bill_id}")
def update_bill(
    bill_id: int,
    bill: BillingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("billing")
    )
):
    existing_bill = (
        db.query(Billing)
        .filter(Billing.id == bill_id)
        .first()
    )

    if not existing_bill:
        raise HTTPException(
            status_code=404,
            detail="Billing record not found"
        )

    existing_bill.patient_id = bill.patient_id
    existing_bill.appointment_id = bill.appointment_id
    existing_bill.bill_date = bill.bill_date
    existing_bill.consultation_fee = bill.consultation_fee
    existing_bill.lab_charges = bill.lab_charges
    existing_bill.medicine_charges = bill.medicine_charges
    existing_bill.other_charges = bill.other_charges
    existing_bill.total_amount = bill.total_amount
    existing_bill.payment_status = bill.payment_status
    existing_bill.payment_method = bill.payment_method

    try:
        db.commit()
        db.refresh(existing_bill)

        return existing_bill

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Billing record could not be updated because of a database conflict"
        )


# =========================
# DELETE BILLING RECORD
# =========================

@router.delete("/{bill_id}")
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("billing")
    )
):
    existing_bill = (
        db.query(Billing)
        .filter(Billing.id == bill_id)
        .first()
    )

    if not existing_bill:
        raise HTTPException(
            status_code=404,
            detail="Billing record not found"
        )

    try:
        db.delete(existing_bill)
        db.commit()

        return {
            "message": "Billing record deleted successfully",
            "bill_id": bill_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Billing record could not be deleted because of a database conflict"
        )