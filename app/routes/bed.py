from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import date

from app.database import SessionLocal
from app.models.bed import Bed
from app.auth import require_permission


router = APIRouter(
    prefix="/beds",
    tags=["Beds"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class BedCreate(BaseModel):
    ward_id: int
    bed_number: str
    bed_type: str | None = None
    status: str = "Available"
    patient_id: int | None = None
    admission_date: date | None = None
    discharge_date: date | None = None


# =========================
# GET ALL BEDS
# =========================

@router.get("/")
def get_beds(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("beds"))
):
    return db.query(Bed).all()


# =========================
# GET BED BY ID
# =========================

@router.get("/{bed_id}")
def get_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("beds"))
):
    bed = (
        db.query(Bed)
        .filter(Bed.id == bed_id)
        .first()
    )

    if not bed:
        raise HTTPException(
            status_code=404,
            detail="Bed not found"
        )

    return bed


# =========================
# CREATE BED
# =========================

@router.post("/")
def create_bed(
    bed: BedCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("beds"))
):
    new_bed = Bed(
        ward_id=bed.ward_id,
        bed_number=bed.bed_number,
        bed_type=bed.bed_type,
        status=bed.status,
        patient_id=bed.patient_id,
        admission_date=bed.admission_date,
        discharge_date=bed.discharge_date
    )

    try:
        db.add(new_bed)
        db.commit()
        db.refresh(new_bed)

        return new_bed

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Bed could not be created because of a database conflict"
        )


# =========================
# UPDATE BED
# =========================

@router.put("/{bed_id}")
def update_bed(
    bed_id: int,
    bed: BedCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("beds"))
):
    existing_bed = (
        db.query(Bed)
        .filter(Bed.id == bed_id)
        .first()
    )

    if not existing_bed:
        raise HTTPException(
            status_code=404,
            detail="Bed not found"
        )

    existing_bed.ward_id = bed.ward_id
    existing_bed.bed_number = bed.bed_number
    existing_bed.bed_type = bed.bed_type
    existing_bed.status = bed.status
    existing_bed.patient_id = bed.patient_id
    existing_bed.admission_date = bed.admission_date
    existing_bed.discharge_date = bed.discharge_date

    try:
        db.commit()
        db.refresh(existing_bed)

        return existing_bed

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Bed could not be updated because of a database conflict"
        )


# =========================
# DELETE BED
# =========================

@router.delete("/{bed_id}")
def delete_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("beds"))
):
    existing_bed = (
        db.query(Bed)
        .filter(Bed.id == bed_id)
        .first()
    )

    if not existing_bed:
        raise HTTPException(
            status_code=404,
            detail="Bed not found"
        )

    try:
        db.delete(existing_bed)
        db.commit()

        return {
            "message": "Bed deleted successfully",
            "bed_id": bed_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Bed cannot be deleted because related records exist"
        )