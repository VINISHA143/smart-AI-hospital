from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field

from app.database import SessionLocal
from app.models.doctor import Doctor
from app.models.user import User
from app.auth import require_permission


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
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

class DoctorCreate(BaseModel):
    user_id: int | None = None
    first_name: str
    last_name: str
    specialization: str
    phone: str | None = None
    email: str | None = None
    license_number: str | None = None

    experience_years: int = Field(
        default=0,
        ge=0
    )

    consultation_fee: float = Field(
        default=0.0,
        ge=0
    )

    availability_status: bool = True


# =========================
# GET ALL DOCTORS
# =========================

@router.get("/")
def get_doctors(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("doctors")
    )
):
    return db.query(Doctor).all()


# =========================
# GET DOCTOR BY ID
# =========================

@router.get("/{doctor_id}")
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("doctors")
    )
):
    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


# =========================
# CREATE DOCTOR
# =========================

@router.post("/")
def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("doctors")
    )
):
    # -------------------------
    # Check user
    # -------------------------

    if doctor.user_id is not None:
        user = (
            db.query(User)
            .filter(User.id == doctor.user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Prevent same user from being assigned
        # to multiple doctors
        existing_user_doctor = (
            db.query(Doctor)
            .filter(Doctor.user_id == doctor.user_id)
            .first()
        )

        if existing_user_doctor:
            raise HTTPException(
                status_code=409,
                detail="This user is already linked to a doctor"
            )

    # -------------------------
    # Check license number
    # -------------------------

    if doctor.license_number:
        existing_license = (
            db.query(Doctor)
            .filter(
                Doctor.license_number == doctor.license_number
            )
            .first()
        )

        if existing_license:
            raise HTTPException(
                status_code=409,
                detail="License number already exists"
            )

    # -------------------------
    # Create doctor
    # -------------------------

    new_doctor = Doctor(
        user_id=doctor.user_id,
        first_name=doctor.first_name,
        last_name=doctor.last_name,
        specialization=doctor.specialization,
        phone=doctor.phone,
        email=doctor.email,
        license_number=doctor.license_number,
        experience_years=doctor.experience_years,
        consultation_fee=doctor.consultation_fee,
        availability_status=doctor.availability_status
    )

    try:
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)

        return new_doctor

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Doctor could not be created because of a database conflict"
        )


# =========================
# UPDATE DOCTOR
# =========================

@router.put("/{doctor_id}")
def update_doctor(
    doctor_id: int,
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("doctors")
    )
):
    # -------------------------
    # Find doctor
    # -------------------------

    existing_doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not existing_doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # -------------------------
    # Check user
    # -------------------------

    if doctor.user_id is not None:
        user = (
            db.query(User)
            .filter(User.id == doctor.user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Check whether another doctor already
        # uses this user
        existing_user_doctor = (
            db.query(Doctor)
            .filter(
                Doctor.user_id == doctor.user_id,
                Doctor.id != doctor_id
            )
            .first()
        )

        if existing_user_doctor:
            raise HTTPException(
                status_code=409,
                detail="This user is already linked to another doctor"
            )

    # -------------------------
    # Check license number
    # -------------------------

    if doctor.license_number:
        existing_license = (
            db.query(Doctor)
            .filter(
                Doctor.license_number == doctor.license_number,
                Doctor.id != doctor_id
            )
            .first()
        )

        if existing_license:
            raise HTTPException(
                status_code=409,
                detail="License number already exists"
            )

    # -------------------------
    # Update doctor
    # -------------------------

    existing_doctor.user_id = doctor.user_id
    existing_doctor.first_name = doctor.first_name
    existing_doctor.last_name = doctor.last_name
    existing_doctor.specialization = doctor.specialization
    existing_doctor.phone = doctor.phone
    existing_doctor.email = doctor.email
    existing_doctor.license_number = doctor.license_number
    existing_doctor.experience_years = doctor.experience_years
    existing_doctor.consultation_fee = doctor.consultation_fee
    existing_doctor.availability_status = doctor.availability_status

    try:
        db.commit()
        db.refresh(existing_doctor)

        return existing_doctor

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Doctor could not be updated because of a database conflict"
        )


# =========================
# DELETE DOCTOR
# =========================

@router.delete("/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("doctors")
    )
):
    # -------------------------
    # Find doctor
    # -------------------------

    existing_doctor = (
        db.query(Doctor)
        .filter(Doctor.id == doctor_id)
        .first()
    )

    if not existing_doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # -------------------------
    # Delete doctor
    # -------------------------

    try:
        db.delete(existing_doctor)
        db.commit()

        return {
            "message": "Doctor deleted successfully",
            "doctor_id": doctor_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Doctor cannot be deleted because related records exist"
        )