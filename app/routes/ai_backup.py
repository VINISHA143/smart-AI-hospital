from typing import List, Dict, Any
import inspect

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.auth import require_permission

from app.ai.symptom_analyzer import analyze_symptoms
from app.ai.disease_risk import calculate_risk
from app.ai.medical_report_analyzer import analyze_medical_report
from app.ai.prescription_checker import check_prescription
from app.ai.emergency_triage import triage_emergency
from app.ai.appointment_recommender import recommend_appointment
from app.ai.health_risk_score import calculate_health_risk
from app.ai.patient_summary import generate_patient_summary
from app.ai.medical_chat import generate_chat_response
from app.ai.clinical_decision_support import (
    generate_clinical_decision_support
)
from app.ai.hospital_analytics import (
    calculate_hospital_analytics
)
from app.ai.resource_prediction import (
    predict_hospital_resources
)
from app.ai.readmission_prediction import (
    calculate_readmission_risk
)
from app.ai.discharge_risk import (
    calculate_discharge_risk
)
from app.ai.care_plan_recommendation import (
    generate_care_plan
)
from app.ai.patient_monitoring import monitor_patient
from app.ai.patient_deterioration import (
    calculate_deterioration_risk
)
from app.ai.medication_adherence import (
    calculate_medication_adherence_risk
)
from app.ai.appointment_no_show import (
    calculate_appointment_no_show_risk
)
from app.ai.patient_flow_prediction import (
    calculate_patient_flow
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


def _call_ai_function(func, payload: Dict[str, Any]):
    """
    Call an AI engine using its actual Python signature.

    This prevents the route layer from assuming that every AI engine
    accepts the same arguments. It also gives a useful error if an
    engine's signature is incompatible with the API payload.
    """
    signature = inspect.signature(func)
    parameters = [
        p for p in signature.parameters.values()
        if p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
    ]

    # If the engine accepts exactly one argument, pass the complete
    # request dictionary. This matches the current symptom analyzer.
    if len(parameters) == 1:
        parameter = parameters[0]
        if parameter.name in payload:
            return func(payload[parameter.name])
        return func(payload)

    aliases = {
        "risk_factors": "medical_history",
        "conditions": "medical_conditions",
        "preferred_department": "department",
    }

    kwargs: Dict[str, Any] = {}
    missing = []

    for parameter in parameters:
        if parameter.name in payload:
            kwargs[parameter.name] = payload[parameter.name]
        elif parameter.name in aliases and aliases[parameter.name] in payload:
            kwargs[parameter.name] = payload[aliases[parameter.name]]
        elif parameter.default is inspect.Parameter.empty:
            missing.append(parameter.name)

    if not missing:
        return func(**kwargs)

    raise TypeError(
        f"{func.__name__} requires parameters {missing}, "
        f"but the API payload contains {sorted(payload.keys())}. "
        f"Update the route payload or the AI function signature."
    )


# ============================================================
# 1. SYMPTOM ANALYZER
# ============================================================

class SymptomRequest(BaseModel):
    symptoms: List[str] = Field(default_factory=list)
    age: int = Field(..., ge=0)
    gender: str = ""
    duration_days: int = Field(default=1, ge=0)


@router.post("/symptom-analyzer")
def symptom_analyzer(
    request: SymptomRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    symptom_payload = {
        "symptoms": request.symptoms,
        "age": request.age,
        "gender": request.gender,
        "duration_days": request.duration_days,
    }

    result = _call_ai_function(
        analyze_symptoms,
        symptom_payload,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 2. DISEASE RISK PREDICTION
# ============================================================

class DiseaseRiskRequest(BaseModel):
    symptoms: List[str] = Field(default_factory=list)
    age: int = Field(..., ge=0)
    gender: str = ""
    medical_history: List[str] = Field(
        default_factory=list
    )


@router.post("/disease-risk")
def disease_risk(
    request: DiseaseRiskRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    result = calculate_risk(
        age=request.age,
        symptoms=request.symptoms,
        risk_factors=request.medical_history,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 3. MEDICAL REPORT ANALYZER
# ============================================================

class MedicalReportParameter(BaseModel):
    name: str
    value: float


class MedicalReportRequest(BaseModel):
    parameters: List[MedicalReportParameter] = Field(
        default_factory=list
    )


@router.post("/medical-report-analyzer")
def medical_report_analyzer(
    request: MedicalReportRequest,
    current_user: dict = Depends(
        require_permission("lab_reports")
    ),
):
    parameters = [
        {
            "name": item.name,
            "value": item.value,
        }
        for item in request.parameters
    ]

    result = analyze_medical_report(
        parameters
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 4. PRESCRIPTION SAFETY CHECKER
# ============================================================

class PrescriptionMedicine(BaseModel):
    name: str
    dose_mg: float = Field(..., ge=0)
    frequency_per_day: int = Field(
        default=1,
        ge=1
    )


class PrescriptionCheckRequest(BaseModel):
    medicines: List[PrescriptionMedicine] = Field(
        default_factory=list
    )
    allergies: List[str] = Field(
        default_factory=list
    )
    medical_conditions: List[str] = Field(
        default_factory=list
    )


@router.post("/prescription-safety")
def prescription_safety(
    request: PrescriptionCheckRequest,
    current_user: dict = Depends(
        require_permission("prescriptions")
    ),
):
    medicines = [
        {
            "name": item.name,
            "dose_mg": item.dose_mg,
            "frequency_per_day": item.frequency_per_day,
        }
        for item in request.medicines
    ]

    result = check_prescription(
        medicines=medicines,
        allergies=request.allergies,
        conditions=request.medical_conditions,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 5. EMERGENCY TRIAGE
# ============================================================

class EmergencyTriageRequest(BaseModel):
    symptoms: List[str] = Field(
        default_factory=list
    )
    severity: int = Field(
        ...,
        ge=1,
        le=10
    )
    age: int = Field(
        ...,
        ge=0
    )
    consciousness: str = "normal"


@router.post("/emergency-triage")
def emergency_triage(
    request: EmergencyTriageRequest,
    current_user: dict = Depends(
        require_permission("emergency_cases")
    ),
):
    # Current triage engine evaluates symptoms.
    # severity, age and consciousness are retained
    # as API inputs for future clinical-rule expansion.

    result = triage_emergency(
        request.symptoms
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 6. SMART APPOINTMENT RECOMMENDATION
# ============================================================

class AppointmentRecommendationRequest(BaseModel):
    symptoms: List[str] = Field(
        default_factory=list
    )
    department: str = ""
    urgency: str = "Auto"


@router.post("/appointment-recommendation")
def appointment_recommendation(
    request: AppointmentRecommendationRequest,
    current_user: dict = Depends(
        require_permission("appointments")
    ),
):
    preferred_department = (
        request.department.strip()
        if request.department
        else None
    )

    result = recommend_appointment(
        symptoms=request.symptoms,
        urgency=request.urgency,
        preferred_department=preferred_department,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 7. PATIENT HEALTH RISK SCORE
# ============================================================

class HealthRiskRequest(BaseModel):
    age: int = Field(..., ge=0)
    bmi: float = Field(default=0, ge=0)
    blood_pressure: str = ""
    glucose: float = Field(default=0, ge=0)
    cholesterol: float = Field(default=0, ge=0)
    smoking: bool = False
    diabetes: bool = False
    hypertension: bool = False
    heart_disease: bool = False


@router.post("/health-risk-score")
def health_risk_score(
    request: HealthRiskRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    health_payload = {
        "age": request.age,
        "bmi": request.bmi,
        "blood_pressure": request.blood_pressure,
        "glucose": request.glucose,
        "cholesterol": request.cholesterol,
        "smoking": request.smoking,
        "diabetes": request.diabetes,
        "hypertension": request.hypertension,
        "heart_disease": request.heart_disease,
    }

    result = _call_ai_function(
        calculate_health_risk,
        health_payload,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 8. PATIENT HEALTH SUMMARY
# ============================================================

class PatientSummaryRequest(BaseModel):
    symptoms: List[str] = Field(
        default_factory=list
    )
    disease_risk: Dict[str, Any] = Field(
        default_factory=dict
    )
    medical_report: Dict[str, Any] = Field(
        default_factory=dict
    )
    prescription_analysis: Dict[str, Any] = Field(
        default_factory=dict
    )
    triage_analysis: Dict[str, Any] = Field(
        default_factory=dict
    )
    appointment_recommendation: Dict[str, Any] = Field(
        default_factory=dict
    )


@router.post("/patient-summary")
def patient_summary(
    request: PatientSummaryRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    result = generate_patient_summary(
        symptoms=request.symptoms,
        disease_risk=request.disease_risk,
        medical_report=request.medical_report,
        prescription_analysis=(
            request.prescription_analysis
        ),
        triage_analysis=request.triage_analysis,
        appointment_recommendation=(
            request.appointment_recommendation
        ),
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 9. MEDICAL CHAT ASSISTANT
# ============================================================

class MedicalChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000
    )

    context: Dict[str, Any] = Field(
        default_factory=dict
    )

    medical_context: Dict[str, Any] = Field(
        default_factory=dict
    )


@router.post("/medical-chat")
def medical_chat(
    request: MedicalChatRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    result = generate_chat_response(
        request.message,
        request.context,
        request.medical_context,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 10. Clinical Decision Support
# ============================================================

class ClinicalDecisionSupportRequest(BaseModel):
    symptoms: List[str] = Field(default_factory=list)
    diagnoses: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    lab_findings: List[str] = Field(default_factory=list)
    prescription_analysis: Dict[str, Any] = Field(default_factory=dict)
    triage_analysis: Dict[str, Any] = Field(default_factory=dict)
    appointment_recommendation: Dict[str, Any] = Field(
        default_factory=dict
    )


@router.post("/clinical-decision-support")
def clinical_decision_support(
    request: ClinicalDecisionSupportRequest,
    current_user: dict = Depends(
        require_permission("medical_records")
    ),
):
    result = generate_clinical_decision_support(
        request.symptoms,
        request.diagnoses,
        request.medications,
        request.lab_findings,
        request.prescription_analysis,
        request.triage_analysis,
        request.appointment_recommendation,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }

# ============================================================
# 11. HOSPITAL ANALYTICS
# ============================================================

class HospitalAnalyticsRequest(BaseModel):
    total_patients: int = Field(..., ge=0)
    total_doctors: int = Field(..., ge=0)
    total_appointments: int = Field(..., ge=0)
    total_admissions: int = Field(..., ge=0)
    total_discharges: int = Field(..., ge=0)
    total_emergency_cases: int = Field(..., ge=0)
    total_beds: int = Field(..., ge=0)
    occupied_beds: int = Field(..., ge=0)


@router.post("/hospital-analytics")
def hospital_analytics(
    request: HospitalAnalyticsRequest,
    current_user: dict = Depends(
        require_permission("users")
    ),
):
    result = calculate_hospital_analytics(
        request.total_patients,
        request.total_doctors,
        request.total_appointments,
        request.total_admissions,
        request.total_discharges,
        request.total_emergency_cases,
        request.total_beds,
        request.occupied_beds,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 12. RESOURCE & BED DEMAND PREDICTION
# ============================================================

class ResourcePredictionRequest(BaseModel):
    current_patients: int = Field(..., ge=0)

    average_daily_admissions: float = Field(
        ...,
        ge=0
    )

    average_daily_discharges: float = Field(
        ...,
        ge=0
    )

    total_beds: int = Field(
        ...,
        ge=1
    )

    occupied_beds: int = Field(
        ...,
        ge=0
    )

    prediction_days: int = Field(
        default=7,
        ge=1,
        le=365
    )


@router.post("/resource-prediction")
def resource_prediction(
    request: ResourcePredictionRequest,
    current_user: dict = Depends(
        require_permission("users")
    ),
):
    result = predict_hospital_resources(
        request.current_patients,
        request.average_daily_admissions,
        request.average_daily_discharges,
        request.total_beds,
        request.occupied_beds,
        request.prediction_days,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 13. READMISSION RISK PREDICTION
# ============================================================

class ReadmissionRiskRequest(BaseModel):
    age: int = Field(..., ge=0)

    previous_admissions: int = Field(
        ...,
        ge=0
    )

    previous_readmissions: int = Field(
        ...,
        ge=0
    )

    chronic_conditions: List[str] = Field(
        default_factory=list
    )

    length_of_stay: int = Field(
        ...,
        ge=0
    )

    emergency_admission: bool = False


@router.post("/readmission-risk")
def readmission_risk(
    request: ReadmissionRiskRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    result = calculate_readmission_risk(
        request.age,
        request.previous_admissions,
        request.previous_readmissions,
        request.chronic_conditions,
        request.length_of_stay,
        request.emergency_admission,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 14. DISCHARGE RISK & FOLLOW-UP
# ============================================================

class DischargeRiskRequest(BaseModel):
    age: int = Field(..., ge=0)

    length_of_stay: int = Field(
        ...,
        ge=0
    )

    chronic_conditions: List[str] = Field(
        default_factory=list
    )

    abnormal_lab_results: List[str] = Field(
        default_factory=list
    )

    mobility_problem: bool = False

    social_support: str = "adequate"


@router.post("/discharge-risk")
def discharge_risk(
    request: DischargeRiskRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    result = calculate_discharge_risk(
        request.age,
        request.length_of_stay,
        request.chronic_conditions,
        request.abnormal_lab_results,
        request.mobility_problem,
        request.social_support,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 15. PATIENT CARE PLAN
# ============================================================

class CarePlanRequest(BaseModel):
    diagnoses: List[str] = Field(
        default_factory=list
    )

    symptoms: List[str] = Field(
        default_factory=list
    )

    medications: List[str] = Field(
        default_factory=list
    )

    chronic_conditions: List[str] = Field(
        default_factory=list
    )


@router.post("/care-plan")
def care_plan(
    request: CarePlanRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    result = generate_care_plan(
        request.diagnoses,
        request.symptoms,
        request.medications,
        request.chronic_conditions,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 16. PATIENT MONITORING
# ============================================================

class PatientMonitoringRequest(BaseModel):
    heart_rate: float = Field(..., ge=0)
    systolic_bp: float = Field(..., ge=0)
    diastolic_bp: float = Field(..., ge=0)
    temperature: float = Field(..., ge=0)
    oxygen_saturation: float = Field(..., ge=0)
    respiratory_rate: float = Field(..., ge=0)


@router.post("/patient-monitoring")
def patient_monitoring(
    request: PatientMonitoringRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    result = monitor_patient(
        request.heart_rate,
        request.systolic_bp,
        request.diastolic_bp,
        request.temperature,
        request.oxygen_saturation,
        request.respiratory_rate,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 17. PATIENT DETERIORATION PREDICTION
# ============================================================

class PatientDeteriorationRequest(BaseModel):
    heart_rate: float = Field(..., ge=0)
    systolic_bp: float = Field(..., ge=0)
    oxygen_saturation: float = Field(..., ge=0)
    respiratory_rate: float = Field(..., ge=0)
    temperature: float = Field(..., ge=0)
    consciousness: str = "normal"


@router.post("/patient-deterioration")
def patient_deterioration(
    request: PatientDeteriorationRequest,
    current_user: dict = Depends(
        require_permission("patients")
    ),
):
    result = calculate_deterioration_risk(
        request.heart_rate,
        request.systolic_bp,
        request.oxygen_saturation,
        request.respiratory_rate,
        request.temperature,
        request.consciousness,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 18. MEDICATION ADHERENCE RISK
# ============================================================

class MedicationAdherenceRequest(BaseModel):
    missed_doses: int = Field(
        ...,
        ge=0
    )

    total_doses: int = Field(
        ...,
        ge=0
    )

    previous_non_adherence: int = Field(
        ...,
        ge=0
    )

    side_effects: List[str] = Field(
        default_factory=list
    )

    cost_problem: bool = False

    forgetfulness: bool = False


@router.post("/medication-adherence-risk")
def medication_adherence_risk(
    request: MedicationAdherenceRequest,
    current_user: dict = Depends(
        require_permission("prescriptions")
    ),
):
    result = calculate_medication_adherence_risk(
        request.missed_doses,
        request.total_doses,
        request.previous_non_adherence,
        request.side_effects,
        request.cost_problem,
        request.forgetfulness,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 19. APPOINTMENT NO-SHOW RISK
# ============================================================

class AppointmentNoShowRequest(BaseModel):
    previous_no_shows: int = Field(
        ...,
        ge=0
    )

    previous_appointments: int = Field(
        ...,
        ge=0
    )

    rescheduled_appointments: int = Field(
        ...,
        ge=0
    )

    waiting_time_minutes: int = Field(
        ...,
        ge=0
    )

    barriers: List[str] = Field(
        default_factory=list
    )

    appointments_same_day: int = Field(
        ...,
        ge=0
    )

    weekend_appointment: bool = False


@router.post("/appointment-no-show-risk")
def appointment_no_show_risk(
    request: AppointmentNoShowRequest,
    current_user: dict = Depends(
        require_permission("appointments")
    ),
):
    result = calculate_appointment_no_show_risk(
        request.previous_no_shows,
        request.previous_appointments,
        request.rescheduled_appointments,
        request.waiting_time_minutes,
        request.barriers,
        request.appointments_same_day,
        request.weekend_appointment,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }


# ============================================================
# 20. HOSPITAL PATIENT FLOW PREDICTION
# ============================================================

class PatientFlowPredictionRequest(BaseModel):
    current_patients: int = Field(
        ...,
        ge=0
    )

    average_daily_patients: float = Field(
        ...,
        ge=0
    )

    current_admissions: int = Field(
        ...,
        ge=0
    )

    average_daily_admissions: float = Field(
        ...,
        ge=0
    )

    current_discharges: int = Field(
        ...,
        ge=0
    )

    average_daily_discharges: float = Field(
        ...,
        ge=0
    )

    current_emergency_cases: int = Field(
        ...,
        ge=0
    )

    average_daily_emergency_cases: float = Field(
        ...,
        ge=0
    )

    total_beds: int = Field(
        ...,
        ge=1
    )

    occupied_beds: int = Field(
        ...,
        ge=0
    )

    prediction_days: int = Field(
        default=7,
        ge=1,
        le=365
    )


@router.post("/patient-flow-prediction")
def patient_flow_prediction(
    request: PatientFlowPredictionRequest,
    current_user: dict = Depends(
        require_permission("users")
    ),
):
    result = calculate_patient_flow(
        request.current_patients,
        request.average_daily_patients,
        request.current_admissions,
        request.average_daily_admissions,
        request.current_discharges,
        request.average_daily_discharges,
        request.current_emergency_cases,
        request.average_daily_emergency_cases,
        request.total_beds,
        request.occupied_beds,
        request.prediction_days,
    )

    return {
        "success": True,
        "requested_by": current_user["username"],
        "role": current_user["role"],
        "result": result,
    }