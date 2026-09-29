from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field

from app.database import SessionLocal
from app.models.ward import Ward
from app.auth import require_permission


router = APIRouter(
    prefix="/wards",
    tags=["Wards"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class WardCreate(BaseModel):
    ward_name: str
    floor_number: int
    ward_type: str | None = None
    total_beds: int = Field(default=0, ge=0)
    available_beds: int = Field(default=0, ge=0)


# =========================
# GET ALL WARDS
# =========================

@router.get("/")
def get_wards(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("wards"))
):
    return db.query(Ward).all()


# =========================
# GET WARD BY ID
# =========================

@router.get("/{ward_id}")
def get_ward(
    ward_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("wards"))
):
    ward = (
        db.query(Ward)
        .filter(Ward.id == ward_id)
        .first()
    )

    if not ward:
        raise HTTPException(
            status_code=404,
            detail="Ward not found"
        )

    return ward


# =========================
# CREATE WARD
# =========================

@router.post("/")
def create_ward(
    ward: WardCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("wards"))
):
    if ward.available_beds > ward.total_beds:
        raise HTTPException(
            status_code=400,
            detail="Available beds cannot be greater than total beds"
        )

    new_ward = Ward(
        ward_name=ward.ward_name,
        floor_number=ward.floor_number,
        ward_type=ward.ward_type,
        total_beds=ward.total_beds,
        available_beds=ward.available_beds
    )

    try:
        db.add(new_ward)
        db.commit()
        db.refresh(new_ward)

        return new_ward

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Ward could not be created because of a database conflict"
        )


# =========================
# UPDATE WARD
# =========================

@router.put("/{ward_id}")
def update_ward(
    ward_id: int,
    ward: WardCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("wards"))
):
    existing_ward = (
        db.query(Ward)
        .filter(Ward.id == ward_id)
        .first()
    )

    if not existing_ward:
        raise HTTPException(
            status_code=404,
            detail="Ward not found"
        )

    if ward.available_beds > ward.total_beds:
        raise HTTPException(
            status_code=400,
            detail="Available beds cannot be greater than total beds"
        )

    existing_ward.ward_name = ward.ward_name
    existing_ward.floor_number = ward.floor_number
    existing_ward.ward_type = ward.ward_type
    existing_ward.total_beds = ward.total_beds
    existing_ward.available_beds = ward.available_beds

    try:
        db.commit()
        db.refresh(existing_ward)

        return existing_ward

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Ward could not be updated because of a database conflict"
        )


# =========================
# DELETE WARD
# =========================

@router.delete("/{ward_id}")
def delete_ward(
    ward_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("wards"))
):
    existing_ward = (
        db.query(Ward)
        .filter(Ward.id == ward_id)
        .first()
    )

    if not existing_ward:
        raise HTTPException(
            status_code=404,
            detail="Ward not found"
        )

    try:
        db.delete(existing_ward)
        db.commit()

        return {
            "message": "Ward deleted successfully",
            "ward_id": ward_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Ward cannot be deleted because related beds or records exist"
        )