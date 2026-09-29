from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import date

from app.database import SessionLocal
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.auth import require_permission


router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"]
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

class MedicalRecordCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: int | None = None

    visit_date: date

    symptoms: str | None = None
    diagnosis: str | None = None
    treatment: str | None = None
    doctor_notes: str | None = None


# =========================
# GET ALL MEDICAL RECORDS
# =========================

@router.get("/")
def get_medical_records(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("medical_records")
    )
):
    return db.query(MedicalRecord).all()


# =========================
# GET MEDICAL RECORD BY ID
# =========================

@router.get("/{record_id}")
def get_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("medical_records")
    )
):
    record = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == record_id)
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    return record


# =========================
# CREATE MEDICAL RECORD
# =========================

@router.post("/")
def create_medical_record(
    record: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("medical_records")
    )
):
    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == record.patient_id)
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
        .filter(Doctor.id == record.doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # -------------------------
    # Check appointment
    # -------------------------

    if record.appointment_id is not None:

        appointment = (
            db.query(Appointment)
            .filter(
                Appointment.id == record.appointment_id
            )
            .first()
        )

        if not appointment:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found"
            )

        # Make sure appointment belongs
        # to the same patient
        if appointment.patient_id != record.patient_id:
            raise HTTPException(
                status_code=400,
                detail="Appointment does not belong to this patient"
            )

        # Make sure appointment belongs
        # to the same doctor
        if appointment.doctor_id != record.doctor_id:
            raise HTTPException(
                status_code=400,
                detail="Appointment does not belong to this doctor"
            )

    # -------------------------
    # Create medical record
    # -------------------------

    new_record = MedicalRecord(
        patient_id=record.patient_id,
        doctor_id=record.doctor_id,
        appointment_id=record.appointment_id,
        visit_date=record.visit_date,
        symptoms=record.symptoms,
        diagnosis=record.diagnosis,
        treatment=record.treatment,
        doctor_notes=record.doctor_notes
    )

    try:
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return new_record

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Medical record could not be created because of a database conflict"
        )


# =========================
# UPDATE MEDICAL RECORD
# =========================

@router.put("/{record_id}")
def update_medical_record(
    record_id: int,
    record: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("medical_records")
    )
):
    # -------------------------
    # Find record
    # -------------------------

    existing_record = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == record_id)
        .first()
    )

    if not existing_record:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == record.patient_id)
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
        .filter(Doctor.id == record.doctor_id)
        .first()
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    # -------------------------
    # Check appointment
    # -------------------------

    if record.appointment_id is not None:

        appointment = (
            db.query(Appointment)
            .filter(
                Appointment.id == record.appointment_id
            )
            .first()
        )

        if not appointment:
            raise HTTPException(
                status_code=404,
                detail="Appointment not found"
            )

        if appointment.patient_id != record.patient_id:
            raise HTTPException(
                status_code=400,
                detail="Appointment does not belong to this patient"
            )

        if appointment.doctor_id != record.doctor_id:
            raise HTTPException(
                status_code=400,
                detail="Appointment does not belong to this doctor"
            )

    # -------------------------
    # Update medical record
    # -------------------------

    existing_record.patient_id = record.patient_id
    existing_record.doctor_id = record.doctor_id
    existing_record.appointment_id = record.appointment_id
    existing_record.visit_date = record.visit_date
    existing_record.symptoms = record.symptoms
    existing_record.diagnosis = record.diagnosis
    existing_record.treatment = record.treatment
    existing_record.doctor_notes = record.doctor_notes

    try:
        db.commit()
        db.refresh(existing_record)

        return existing_record

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Medical record could not be updated because of a database conflict"
        )


# =========================
# DELETE MEDICAL RECORD
# =========================

@router.delete("/{record_id}")
def delete_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("medical_records")
    )
):
    # -------------------------
    # Find record
    # -------------------------

    existing_record = (
        db.query(MedicalRecord)
        .filter(MedicalRecord.id == record_id)
        .first()
    )

    if not existing_record:
        raise HTTPException(
            status_code=404,
            detail="Medical record not found"
        )

    # -------------------------
    # Delete record
    # -------------------------

    try:
        db.delete(existing_record)
        db.commit()

        return {
            "message": "Medical record deleted successfully",
            "record_id": record_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Medical record cannot be deleted because related records exist"
        )