from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import date, time

from app.database import SessionLocal
from app.models.emergency_case import EmergencyCase
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.auth import require_permission


router = APIRouter(
    prefix="/emergency-cases",
    tags=["Emergency Cases"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class EmergencyCaseCreate(BaseModel):
    patient_id: int
    doctor_id: int | None = None
    emergency_reason: str
    severity: str
    status: str = "Open"
    symptoms: str | None = None
    treatment_notes: str | None = None
    emergency_date: date | None = None
    emergency_time: time | None = None


# =========================
# GET ALL EMERGENCY CASES
# =========================

@router.get("/")
def get_emergency_cases(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("emergency_cases")
    )
):
    return db.query(EmergencyCase).all()


# =========================
# GET EMERGENCY CASE BY ID
# =========================

@router.get("/{case_id}")
def get_emergency_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("emergency_cases")
    )
):
    emergency_case = (
        db.query(EmergencyCase)
        .filter(EmergencyCase.id == case_id)
        .first()
    )

    if not emergency_case:
        raise HTTPException(
            status_code=404,
            detail="Emergency case not found"
        )

    return emergency_case


# =========================
# CREATE EMERGENCY CASE
# =========================

@router.post("/")
def create_emergency_case(
    emergency_case: EmergencyCaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("emergency_cases")
    )
):
    # Validate patient
    patient = (
        db.query(Patient)
        .filter(Patient.id == emergency_case.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Validate doctor if supplied
    if emergency_case.doctor_id is not None:
        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == emergency_case.doctor_id)
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

    new_emergency_case = EmergencyCase(
        patient_id=emergency_case.patient_id,
        doctor_id=emergency_case.doctor_id,
        emergency_reason=emergency_case.emergency_reason,
        severity=emergency_case.severity,
        status=emergency_case.status,
        symptoms=emergency_case.symptoms,
        treatment_notes=emergency_case.treatment_notes
    )

    # Only set these if the model contains them
    if hasattr(EmergencyCase, "emergency_date"):
        new_emergency_case.emergency_date = (
            emergency_case.emergency_date
        )

    if hasattr(EmergencyCase, "emergency_time"):
        new_emergency_case.emergency_time = (
            emergency_case.emergency_time
        )

    try:
        db.add(new_emergency_case)
        db.commit()
        db.refresh(new_emergency_case)

        return new_emergency_case

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Emergency case could not be created "
                "because of a database conflict"
            )
        )


# =========================
# UPDATE EMERGENCY CASE
# =========================

@router.put("/{case_id}")
def update_emergency_case(
    case_id: int,
    emergency_case: EmergencyCaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("emergency_cases")
    )
):
    existing_case = (
        db.query(EmergencyCase)
        .filter(EmergencyCase.id == case_id)
        .first()
    )

    if not existing_case:
        raise HTTPException(
            status_code=404,
            detail="Emergency case not found"
        )

    # Validate patient
    patient = (
        db.query(Patient)
        .filter(Patient.id == emergency_case.patient_id)
        .first()
    )

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    # Validate doctor if supplied
    if emergency_case.doctor_id is not None:
        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == emergency_case.doctor_id)
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

    existing_case.patient_id = emergency_case.patient_id
    existing_case.doctor_id = emergency_case.doctor_id
    existing_case.emergency_reason = emergency_case.emergency_reason
    existing_case.severity = emergency_case.severity
    existing_case.status = emergency_case.status
    existing_case.symptoms = emergency_case.symptoms
    existing_case.treatment_notes = emergency_case.treatment_notes

    if hasattr(EmergencyCase, "emergency_date"):
        existing_case.emergency_date = (
            emergency_case.emergency_date
        )

    if hasattr(EmergencyCase, "emergency_time"):
        existing_case.emergency_time = (
            emergency_case.emergency_time
        )

    try:
        db.commit()
        db.refresh(existing_case)

        return existing_case

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Emergency case could not be updated "
                "because of a database conflict"
            )
        )


# =========================
# DELETE EMERGENCY CASE
# =========================

@router.delete("/{case_id}")
def delete_emergency_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("emergency_cases")
    )
):
    existing_case = (
        db.query(EmergencyCase)
        .filter(EmergencyCase.id == case_id)
        .first()
    )

    if not existing_case:
        raise HTTPException(
            status_code=404,
            detail="Emergency case not found"
        )

    try:
        db.delete(existing_case)
        db.commit()

        return {
            "message": "Emergency case deleted successfully",
            "case_id": case_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "Emergency case cannot be deleted "
                "because related records exist"
            )
        )