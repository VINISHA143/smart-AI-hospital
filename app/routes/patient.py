from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import date

from app.database import SessionLocal
from app.models.patient import Patient
from app.auth import require_permission


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
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

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date | None = None
    gender: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    blood_group: str | None = None
    emergency_contact: str | None = None


# =========================
# GET ALL PATIENTS
# =========================

@router.get("/")
def get_patients(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("patients")
    )
):
    return db.query(Patient).all()


# =========================
# GET PATIENT BY ID
# =========================

@router.get("/{patient_id}")
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("patients")
    )
):
    patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient


# =========================
# CREATE PATIENT
# =========================

@router.post("/")
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("patients")
    )
):
    new_patient = Patient(
        first_name=patient.first_name,
        last_name=patient.last_name,
        date_of_birth=patient.date_of_birth,
        gender=patient.gender,
        phone=patient.phone,
        email=patient.email,
        address=patient.address,
        blood_group=patient.blood_group,
        emergency_contact=patient.emergency_contact
    )

    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        return new_patient

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Patient could not be created because of a database conflict"
        )


# =========================
# UPDATE PATIENT
# =========================

@router.put("/{patient_id}")
def update_patient(
    patient_id: int,
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("patients")
    )
):
    existing_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not existing_patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    existing_patient.first_name = patient.first_name
    existing_patient.last_name = patient.last_name
    existing_patient.date_of_birth = patient.date_of_birth
    existing_patient.gender = patient.gender
    existing_patient.phone = patient.phone
    existing_patient.email = patient.email
    existing_patient.address = patient.address
    existing_patient.blood_group = patient.blood_group
    existing_patient.emergency_contact = patient.emergency_contact

    try:
        db.commit()
        db.refresh(existing_patient)

        return existing_patient

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Patient could not be updated because of a database conflict"
        )


# =========================
# DELETE PATIENT
# =========================

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("patients")
    )
):
    existing_patient = (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )

    if not existing_patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    try:
        db.delete(existing_patient)
        db.commit()

        return {
            "message": "Patient deleted successfully",
            "patient_id": patient_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Patient cannot be deleted because related records exist"
        )