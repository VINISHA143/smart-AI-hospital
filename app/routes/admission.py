from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import date, time

from app.database import SessionLocal
from app.models.admission import Admission
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.auth import require_permission


router = APIRouter(
    prefix="/admissions",
    tags=["Admissions"]
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

class AdmissionCreate(BaseModel):
    patient_id: int
    doctor_id: int | None = None
    bed_id: int | None = None

    admission_date: date
    admission_time: time | None = None

    reason: str | None = None
    diagnosis: str | None = None

    status: str = "Admitted"

    discharge_date: date | None = None
    discharge_notes: str | None = None


# =========================
# GET ALL ADMISSIONS
# =========================

@router.get("/")
def get_admissions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("admissions")
    )
):
    return db.query(Admission).all()


# =========================
# GET ADMISSION BY ID
# =========================

@router.get("/{admission_id}")
def get_admission(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("admissions")
    )
):
    admission = (
        db.query(Admission)
        .filter(Admission.id == admission_id)
        .first()
    )

    if not admission:
        raise HTTPException(
            status_code=404,
            detail="Admission not found"
        )

    return admission


# =========================
# CREATE ADMISSION
# =========================

@router.post("/")
def create_admission(
    admission: AdmissionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("admissions")
    )
):
    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == admission.patient_id)
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

    if admission.doctor_id is not None:

        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == admission.doctor_id)
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found"
            )

        # -------------------------
        # Check doctor availability
        # -------------------------

        if not doctor.availability_status:
            raise HTTPException(
                status_code=400,
                detail="Doctor is currently unavailable"
            )

    # -------------------------
    # Validate discharge date
    # -------------------------

    if (
        admission.discharge_date is not None
        and admission.discharge_date < admission.admission_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Discharge date cannot be before admission date"
        )

    # -------------------------
    # Create admission
    # -------------------------

    new_admission = Admission(
        patient_id=admission.patient_id,
        doctor_id=admission.doctor_id,
        bed_id=admission.bed_id,
        admission_date=admission.admission_date,
        admission_time=admission.admission_time,
        reason=admission.reason,
        diagnosis=admission.diagnosis,
        status=admission.status,
        discharge_date=admission.discharge_date,
        discharge_notes=admission.discharge_notes
    )

    try:
        db.add(new_admission)
        db.commit()
        db.refresh(new_admission)

        return new_admission

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Admission could not be created because of a database conflict"
        )


# =========================
# UPDATE ADMISSION
# =========================

@router.put("/{admission_id}")
def update_admission(
    admission_id: int,
    admission: AdmissionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("admissions")
    )
):
    # -------------------------
    # Find admission
    # -------------------------

    existing_admission = (
        db.query(Admission)
        .filter(Admission.id == admission_id)
        .first()
    )

    if not existing_admission:
        raise HTTPException(
            status_code=404,
            detail="Admission not found"
        )

    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == admission.patient_id)
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

    if admission.doctor_id is not None:

        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == admission.doctor_id)
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found"
            )

        if not doctor.availability_status:
            raise HTTPException(
                status_code=400,
                detail="Doctor is currently unavailable"
            )

    # -------------------------
    # Validate discharge date
    # -------------------------

    if (
        admission.discharge_date is not None
        and admission.discharge_date < admission.admission_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Discharge date cannot be before admission date"
        )

    # -------------------------
    # Update admission
    # -------------------------

    existing_admission.patient_id = admission.patient_id
    existing_admission.doctor_id = admission.doctor_id
    existing_admission.bed_id = admission.bed_id
    existing_admission.admission_date = admission.admission_date
    existing_admission.admission_time = admission.admission_time
    existing_admission.reason = admission.reason
    existing_admission.diagnosis = admission.diagnosis
    existing_admission.status = admission.status
    existing_admission.discharge_date = admission.discharge_date
    existing_admission.discharge_notes = admission.discharge_notes

    try:
        db.commit()
        db.refresh(existing_admission)

        return existing_admission

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Admission could not be updated because of a database conflict"
        )


# =========================
# DELETE ADMISSION
# =========================

@router.delete("/{admission_id}")
def delete_admission(
    admission_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("admissions")
    )
):
    # -------------------------
    # Find admission
    # -------------------------

    existing_admission = (
        db.query(Admission)
        .filter(Admission.id == admission_id)
        .first()
    )

    if not existing_admission:
        raise HTTPException(
            status_code=404,
            detail="Admission not found"
        )

    # -------------------------
    # Delete admission
    # -------------------------

    try:
        db.delete(existing_admission)
        db.commit()

        return {
            "message": "Admission deleted successfully",
            "admission_id": admission_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Admission cannot be deleted because related records exist"
        )