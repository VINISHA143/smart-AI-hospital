from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import date, time

from app.database import SessionLocal
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.auth import require_permission


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
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

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    reason: str | None = None
    status: str = "Scheduled"
    notes: str | None = None


# =========================
# GET ALL APPOINTMENTS
# =========================

@router.get("/")
def get_appointments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("appointments")
    )
):
    return db.query(Appointment).all()


# =========================
# GET APPOINTMENT BY ID
# =========================

@router.get("/{appointment_id}")
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("appointments")
    )
):
    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return appointment


# =========================
# CREATE APPOINTMENT
# =========================

@router.post("/")
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("appointments")
    )
):
    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == appointment.patient_id)
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
        .filter(Doctor.id == appointment.doctor_id)
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
    # Create appointment
    # -------------------------

    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        reason=appointment.reason,
        status=appointment.status,
        notes=appointment.notes
    )

    try:
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)

        return new_appointment

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Appointment could not be created because of a database conflict"
        )


# =========================
# UPDATE APPOINTMENT
# =========================

@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("appointments")
    )
):
    # -------------------------
    # Find appointment
    # -------------------------

    existing_appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not existing_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == appointment.patient_id)
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
        .filter(Doctor.id == appointment.doctor_id)
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
    # Update appointment
    # -------------------------

    existing_appointment.patient_id = appointment.patient_id
    existing_appointment.doctor_id = appointment.doctor_id
    existing_appointment.appointment_date = appointment.appointment_date
    existing_appointment.appointment_time = appointment.appointment_time
    existing_appointment.reason = appointment.reason
    existing_appointment.status = appointment.status
    existing_appointment.notes = appointment.notes

    try:
        db.commit()
        db.refresh(existing_appointment)

        return existing_appointment

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Appointment could not be updated because of a database conflict"
        )


# =========================
# DELETE APPOINTMENT
# =========================

@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("appointments")
    )
):
    # -------------------------
    # Find appointment
    # -------------------------

    existing_appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if not existing_appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    # -------------------------
    # Delete appointment
    # -------------------------

    try:
        db.delete(existing_appointment)
        db.commit()

        return {
            "message": "Appointment deleted successfully",
            "appointment_id": appointment_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Appointment cannot be deleted because related records exist"
        )