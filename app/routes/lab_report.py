from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import date

from app.database import SessionLocal
from app.models.lab_report import LabReport
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.auth import require_permission


router = APIRouter(
    prefix="/lab-reports",
    tags=["Lab Reports"]
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

class LabReportCreate(BaseModel):
    patient_id: int
    doctor_id: int | None = None

    test_name: str
    test_date: date

    result_value: str | None = None
    unit: str | None = None
    reference_range: str | None = None

    report_status: str = "Completed"
    remarks: str | None = None


# =========================
# GET ALL LAB REPORTS
# =========================

@router.get("/")
def get_lab_reports(
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("lab_reports")
    )
):
    return db.query(LabReport).all()


# =========================
# GET LAB REPORT BY ID
# =========================

@router.get("/{report_id}")
def get_lab_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("lab_reports")
    )
):
    report = (
        db.query(LabReport)
        .filter(LabReport.id == report_id)
        .first()
    )

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Lab report not found"
        )

    return report


# =========================
# CREATE LAB REPORT
# =========================

@router.post("/")
def create_lab_report(
    report: LabReportCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("lab_reports")
    )
):
    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == report.patient_id)
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

    if report.doctor_id is not None:

        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == report.doctor_id)
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found"
            )

    # -------------------------
    # Create lab report
    # -------------------------

    new_report = LabReport(
        patient_id=report.patient_id,
        doctor_id=report.doctor_id,
        test_name=report.test_name,
        test_date=report.test_date,
        result_value=report.result_value,
        unit=report.unit,
        reference_range=report.reference_range,
        report_status=report.report_status,
        remarks=report.remarks
    )

    try:
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        return new_report

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Lab report could not be created because of a database conflict"
        )


# =========================
# UPDATE LAB REPORT
# =========================

@router.put("/{report_id}")
def update_lab_report(
    report_id: int,
    report: LabReportCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("lab_reports")
    )
):
    # -------------------------
    # Find report
    # -------------------------

    existing_report = (
        db.query(LabReport)
        .filter(LabReport.id == report_id)
        .first()
    )

    if not existing_report:
        raise HTTPException(
            status_code=404,
            detail="Lab report not found"
        )

    # -------------------------
    # Check patient
    # -------------------------

    patient = (
        db.query(Patient)
        .filter(Patient.id == report.patient_id)
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

    if report.doctor_id is not None:

        doctor = (
            db.query(Doctor)
            .filter(Doctor.id == report.doctor_id)
            .first()
        )

        if not doctor:
            raise HTTPException(
                status_code=404,
                detail="Doctor not found"
            )

    # -------------------------
    # Update report
    # -------------------------

    existing_report.patient_id = report.patient_id
    existing_report.doctor_id = report.doctor_id
    existing_report.test_name = report.test_name
    existing_report.test_date = report.test_date
    existing_report.result_value = report.result_value
    existing_report.unit = report.unit
    existing_report.reference_range = report.reference_range
    existing_report.report_status = report.report_status
    existing_report.remarks = report.remarks

    try:
        db.commit()
        db.refresh(existing_report)

        return existing_report

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Lab report could not be updated because of a database conflict"
        )


# =========================
# DELETE LAB REPORT
# =========================

@router.delete("/{report_id}")
def delete_lab_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_permission("lab_reports")
    )
):
    # -------------------------
    # Find report
    # -------------------------

    existing_report = (
        db.query(LabReport)
        .filter(LabReport.id == report_id)
        .first()
    )

    if not existing_report:
        raise HTTPException(
            status_code=404,
            detail="Lab report not found"
        )

    # -------------------------
    # Delete report
    # -------------------------

    try:
        db.delete(existing_report)
        db.commit()

        return {
            "message": "Lab report deleted successfully",
            "report_id": report_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Lab report cannot be deleted because related records exist"
        )