from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal

from app.database import SessionLocal
from app.models.medicine import Medicine
from app.auth import require_permission


router = APIRouter(
    prefix="/medicines",
    tags=["Medicines"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MedicineCreate(BaseModel):
    medicine_name: str
    category: str | None = None
    manufacturer: str | None = None
    batch_number: str | None = None
    quantity: int = Field(default=0, ge=0)
    unit_price: Decimal = Field(default=Decimal("0.00"), ge=0)
    expiry_date: date | None = None
    supplier_name: str | None = None


# =========================
# GET ALL MEDICINES
# =========================

@router.get("/")
def get_medicines(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("medicines"))
):
    return db.query(Medicine).all()


# =========================
# GET MEDICINE BY ID
# =========================

@router.get("/{medicine_id}")
def get_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("medicines"))
):
    medicine = (
        db.query(Medicine)
        .filter(Medicine.id == medicine_id)
        .first()
    )

    if not medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    return medicine


# =========================
# CREATE MEDICINE
# =========================

@router.post("/")
def create_medicine(
    medicine: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("medicines"))
):
    new_medicine = Medicine(
        medicine_name=medicine.medicine_name,
        category=medicine.category,
        manufacturer=medicine.manufacturer,
        batch_number=medicine.batch_number,
        quantity=medicine.quantity,
        unit_price=medicine.unit_price,
        expiry_date=medicine.expiry_date,
        supplier_name=medicine.supplier_name
    )

    try:
        db.add(new_medicine)
        db.commit()
        db.refresh(new_medicine)

        return new_medicine

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Medicine could not be created because of a database conflict"
        )


# =========================
# UPDATE MEDICINE
# =========================

@router.put("/{medicine_id}")
def update_medicine(
    medicine_id: int,
    medicine: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("medicines"))
):
    existing_medicine = (
        db.query(Medicine)
        .filter(Medicine.id == medicine_id)
        .first()
    )

    if not existing_medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    existing_medicine.medicine_name = medicine.medicine_name
    existing_medicine.category = medicine.category
    existing_medicine.manufacturer = medicine.manufacturer
    existing_medicine.batch_number = medicine.batch_number
    existing_medicine.quantity = medicine.quantity
    existing_medicine.unit_price = medicine.unit_price
    existing_medicine.expiry_date = medicine.expiry_date
    existing_medicine.supplier_name = medicine.supplier_name

    try:
        db.commit()
        db.refresh(existing_medicine)

        return existing_medicine

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Medicine could not be updated because of a database conflict"
        )


# =========================
# DELETE MEDICINE
# =========================

@router.delete("/{medicine_id}")
def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("medicines"))
):
    existing_medicine = (
        db.query(Medicine)
        .filter(Medicine.id == medicine_id)
        .first()
    )

    if not existing_medicine:
        raise HTTPException(
            status_code=404,
            detail="Medicine not found"
        )

    try:
        db.delete(existing_medicine)
        db.commit()

        return {
            "message": "Medicine deleted successfully",
            "medicine_id": medicine_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Medicine cannot be deleted because related records exist"
        )