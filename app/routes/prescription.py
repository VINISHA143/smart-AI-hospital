from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import date

from app.database import SessionLocal
from app.models.prescription import Prescription
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.medical_record import MedicalRecord
from app.auth import require_permission


router = APIRouter(
    prefix="/prescriptions",
    tags=["Prescriptions"]
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

class PrescriptionCreate(BaseModel):
    patient_id: int
    doctor_id: int
    medical_record_id: int | None = None

    medicine_name: str
    dosage: str | None = None
    frequency: str | None = None
    duration: str | None = None
    instructions: str | None = None

    prescribed_date: date


# =========================
# GET ALL PRESCRIPTIONS
# =========================

@router.get("/")
def get_prescriptions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("prescriptions")
    )
):
    return db.query(Prescription).all()


# =========================
# GET PRESCRIPTION BY ID
# =========================

@router.get("/{prescription_id}")
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("prescriptions")
    )
):
    prescription = (
        db.query(Prescription)
        .filter(Prescription.id == prescription_id)
        .first()
    )

    if not prescription:
        raise HTTPException(
            status_code=404,
            detail="Prescription not found"
        )

    return prescription


# =========================
# CREATE PRESCRIPTION
# =========================

@router.post("/")
def create_prescription(
    prescription: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("prescriptions")
    )
):
    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == prescription.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # -------------------------
    # Check doctor
    # -------------------------

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == prescription.doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # -------------------------
    # Check medical record
    # -------------------------

    if prescription.medical_record_id is not None:

        medical_record = (
            db.query(MedicalRecord)
            .filter(
                MedicalRecord.id
                == prescription.medical_record_id
            )
            .first()
        )

        if not medical_record:
            raise HTTPException(
                status_code=404,
                detail="Medical record not found"
            )

        # Make sure the medical record belongs
        # to the same patient
        if medical_record.patient_id != prescription.patient_id:
            raise HTTPException(
                status_code=400,
                detail="Medical record does not belong to this patient"
            )

        # Make sure the medical record belongs
        # to the same doctor
        if medical_record.doctor_id != prescription.doctor_id:
            raise HTTPException(
                status_code=400,
                detail="Medical record does not belong to this doctor"
            )

    # -------------------------
    # Create prescription
    # -------------------------

    new_prescription = Prescription(
        patient_id=prescription.patient_id,
        doctor_id=prescription.doctor_id,
        medical_record_id=prescription.medical_record_id,
        medicine_name=prescription.medicine_name,
        dosage=prescription.dosage,
        frequency=prescription.frequency,
        duration=prescription.duration,
        instructions=prescription.instructions,
        prescribed_date=prescription.prescribed_date
    )

    try:
        db.add(new_prescription)
        db.commit()
        db.refresh(new_prescription)

        return new_prescription

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Prescription could not be created because of a database conflict"
        )


# =========================
# UPDATE PRESCRIPTION
# =========================

@router.put("/{prescription_id}")
def update_prescription(
    prescription_id: int,
    prescription: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("prescriptions")
    )
):
    # -------------------------
    # Find prescription
    # -------------------------

    existing_prescription = (
        db.query(Prescription)
        .filter(Prescription.id == prescription_id)
        .first()
    )

    if not existing_prescription:
        raise HTTPException(
            status_code=404,
            detail="Prescription not found"
        )

    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == prescription.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # -------------------------
    # Check doctor
    # -------------------------

    doctor = (
        db.query(Doctor)
        .filter(Doctor.id == prescription.doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # -------------------------
    # Check medical record
    # -------------------------

    if prescription.medical_record_id is not None:

        medical_record = (
            db.query(MedicalRecord)
            .filter(
                MedicalRecord.id
                == prescription.medical_record_id
            )
            .first()
        )

        if not medical_record:
            raise HTTPException(
                status_code=404,
                detail="Medical record not found"
            )

        if medical_record.patient_id != prescription.patient_id:
            raise HTTPException(
                status_code=400,
                detail="Medical record does not belong to this patient"
            )

        if medical_record.doctor_id != prescription.doctor_id:
            raise HTTPException(
                status_code=400,
                detail="Medical record does not belong to this doctor"
            )

    # -------------------------
    # Update prescription
    # -------------------------

    existing_prescription.patient_id = prescription.patient_id
    existing_prescription.doctor_id = prescription.doctor_id
    existing_prescription.medical_record_id = (
        prescription.medical_record_id
    )
    existing_prescription.medicine_name = (
        prescription.medicine_name
    )
    existing_prescription.dosage = prescription.dosage
    existing_prescription.frequency = prescription.frequency
    existing_prescription.duration = prescription.duration
    existing_prescription.instructions = prescription.instructions
    existing_prescription.prescribed_date = (
        prescription.prescribed_date
    )

    try:
        db.commit()
        db.refresh(existing_prescription)

        return existing_prescription

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Prescription could not be updated because of a database conflict"
        )


# =========================
# DELETE PRESCRIPTION
# =========================

@router.delete("/{prescription_id}")
def delete_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("prescriptions")
    )
):
    # -------------------------
    # Find prescription
    # -------------------------

    existing_prescription = (
        db.query(Prescription)
        .filter(Prescription.id == prescription_id)
        .first()
    )

    if not existing_prescription:
        raise HTTPException(
            status_code=404,
            detail="Prescription not found"
        )

    # -------------------------
    # Delete prescription
    # -------------------------

    try:
        db.delete(existing_prescription)
        db.commit()

        return {
            "message": "Prescription deleted successfully",
            "prescription_id": prescription_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Prescription cannot be deleted because related records exist"
        )