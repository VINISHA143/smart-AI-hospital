from typing import Any, Dict, List


def _safe_text(value: Any, default: str = "") -> str:
    if value is None:
        return default

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def _extract_symptoms(value: Any) -> List[str]:
    if value is None:
        return []

    if not isinstance(value, list):
        value = [value]

    result: List[str] = []

    for item in value:
        if isinstance(item, str):
            text = item.strip()

            if text:
                result.append(text)

        elif isinstance(item, dict):
            symptom = (
                item.get("symptom")
                or item.get("name")
                or item.get("description")
                or item.get("value")
            )

            if symptom is not None:
                text = _safe_text(symptom)

                if text:
                    result.append(text)

        else:
            text = _safe_text(item)

            if text:
                result.append(text)

    return result


def _extract_abnormal_parameters(value: Any) -> List[str]:
    """
    Supports both:

    ["glucose", "cholesterol"]

    and:

    [
        {"parameter": "glucose"},
        {"parameter": "cholesterol"}
    ]
    """

    if value is None:
        return []

    if not isinstance(value, list):
        value = [value]

    result: List[str] = []

    for item in value:

        # String value
        if isinstance(item, str):
            text = item.strip()

            if text:
                result.append(text)

        # Dictionary value
        elif isinstance(item, dict):
            parameter = (
                item.get("parameter")
                or item.get("name")
                or item.get("test")
                or item.get("label")
                or item.get("value")
            )

            if parameter is not None:
                text = _safe_text(parameter)

                if text:
                    result.append(text)

        # Any other value
        else:
            text = _safe_text(item)

            if text:
                result.append(text)

    return result


def _get_value(
    data: Any,
    *keys: str,
    default: Any = None
) -> Any:

    if not isinstance(data, dict):
        return default

    for key in keys:
        if key in data and data[key] is not None:
            return data[key]

    return default


def generate_patient_summary(
    symptoms: Any,
    disease_risk: Dict[str, Any],
    medical_report: Dict[str, Any],
    prescription_analysis: Dict[str, Any],
    triage_analysis: Dict[str, Any],
    appointment_recommendation: Dict[str, Any],
) -> Dict[str, Any]:

    # ---------------------------------------------------------
    # Normalize input dictionaries
    # ---------------------------------------------------------

    if not isinstance(disease_risk, dict):
        disease_risk = {}

    if not isinstance(medical_report, dict):
        medical_report = {}

    if not isinstance(prescription_analysis, dict):
        prescription_analysis = {}

    if not isinstance(triage_analysis, dict):
        triage_analysis = {}

    if not isinstance(appointment_recommendation, dict):
        appointment_recommendation = {}

    # ---------------------------------------------------------
    # Symptoms
    # ---------------------------------------------------------

    symptoms_list = _extract_symptoms(symptoms)

    # ---------------------------------------------------------
    # Disease risk
    # ---------------------------------------------------------

    risk_score = _get_value(
        disease_risk,
        "risk_score",
        "score",
        default=0,
    )

    risk_level = _get_value(
        disease_risk,
        "risk_level",
        "level",
        default="Unknown",
    )

    # ---------------------------------------------------------
    # Medical report
    # ---------------------------------------------------------

    severity = _get_value(
        medical_report,
        "severity",
        "severity_level",
        default="Unknown",
    )

    abnormal_parameters = _extract_abnormal_parameters(
        medical_report.get(
            "abnormal_parameters",
            []
        )
    )

    # ---------------------------------------------------------
    # Prescription analysis
    # ---------------------------------------------------------

    safety_level = _get_value(
        prescription_analysis,
        "safety_level",
        "safety",
        "risk_level",
        "level",
        default="Unknown",
    )

    warning_count = _get_value(
        prescription_analysis,
        "warning_count",
        "warnings_count",
        default=0,
    )

    warnings = prescription_analysis.get(
        "warnings",
        []
    )

    if warnings is None:
        warnings = []

    if not isinstance(warnings, list):
        warnings = [warnings]

    # ---------------------------------------------------------
    # Triage
    # ---------------------------------------------------------

    triage_level = _get_value(
        triage_analysis,
        "level",
        "triage_level",
        "urgency",
        default="Unknown",
    )

    triage_reason = _get_value(
        triage_analysis,
        "reason",
        "recommendation",
        "message",
        default="",
    )

    # ---------------------------------------------------------
    # Appointment recommendation
    # ---------------------------------------------------------

    department = _get_value(
        appointment_recommendation,
        "department",
        "recommended_department",
        default="General Medicine",
    )

    specialty = _get_value(
        appointment_recommendation,
        "specialty",
        "recommended_specialty",
        default=department,
    )

    # ---------------------------------------------------------
    # Convert values to safe text
    # ---------------------------------------------------------

    risk_score_text = _safe_text(
        risk_score,
        "0"
    )

    risk_level_text = _safe_text(
        risk_level,
        "Unknown"
    )

    severity_text = _safe_text(
        severity,
        "Unknown"
    )

    safety_level_text = _safe_text(
        safety_level,
        "Unknown"
    )

    warning_count_text = _safe_text(
        warning_count,
        "0"
    )

    triage_level_text = _safe_text(
        triage_level,
        "Unknown"
    )

    triage_reason_text = _safe_text(
        triage_reason
    )

    department_text = _safe_text(
        department,
        "General Medicine"
    )

    specialty_text = _safe_text(
        specialty,
        department_text
    )

    # ---------------------------------------------------------
    # Human-readable values
    # ---------------------------------------------------------

    symptom_text = (
        ", ".join(symptoms_list)
        if symptoms_list
        else "No symptoms reported"
    )

    abnormal_text = (
        ", ".join(abnormal_parameters)
        if abnormal_parameters
        else "No abnormal parameters reported"
    )

    # ---------------------------------------------------------
    # Overall status
    # ---------------------------------------------------------

    overall_status = "Stable"

    triage_lower = triage_level_text.lower()
    risk_lower = risk_level_text.lower()
    severity_lower = severity_text.lower()

    if triage_lower in {
        "critical",
        "emergency",
        "immediate",
        "life-threatening",
    }:
        overall_status = "Requires Attention"

    elif risk_lower in {
        "high",
        "critical",
    }:
        overall_status = "Requires Attention"

    elif (
        triage_lower in {
            "urgent",
            "priority",
        }
        or risk_lower in {
            "moderate",
            "medium",
        }
        or severity_lower in {
            "moderate",
            "high",
        }
    ):
        overall_status = "Monitor Closely"

    # ---------------------------------------------------------
    # Summary text
    # ---------------------------------------------------------

    summary_parts = [
        f"Reported symptoms: {symptom_text}.",

        (
            f"Disease risk assessment: "
            f"{risk_level_text} "
            f"with a risk score of "
            f"{risk_score_text}."
        ),

        (
            f"Medical report severity: "
            f"{severity_text}. "
            f"Abnormal parameters: "
            f"{abnormal_text}."
        ),

        (
            f"Prescription safety assessment: "
            f"{safety_level_text} "
            f"with {warning_count_text} warning(s)."
        ),

        (
            f"Emergency triage level: "
            f"{triage_level_text}."
        ),

        (
            f"Recommended department: "
            f"{department_text}. "
            f"Recommended specialty: "
            f"{specialty_text}."
        ),
    ]

    if triage_reason_text:
        summary_parts.append(
            f"Triage recommendation: "
            f"{triage_reason_text}."
        )

    summary = " ".join(summary_parts)

    # ---------------------------------------------------------
    # Final response
    # ---------------------------------------------------------

    return {
        "status": "success",

        "overall_status": overall_status,

        "patient_summary": summary,

        "symptoms": symptoms_list,

        "disease_risk": {
            "risk_score": risk_score,
            "risk_level": risk_level_text,
        },

        "medical_report": {
            "severity": severity_text,
            "abnormal_parameters": abnormal_parameters,
        },

        "prescription_analysis": {
            "safety_level": safety_level_text,
            "warning_count": warning_count,
            "warnings": warnings,
        },

        "triage_analysis": {
            "level": triage_level_text,
            "reason": triage_reason_text,
        },

        "appointment_recommendation": {
            "department": department_text,
            "specialty": specialty_text,
        },

        "recommendations": [
            (
                f"Consider consultation with "
                f"{specialty_text} in the "
                f"{department_text} department."
            ),
            (
                "Review the medical report and "
                "abnormal parameters with a "
                "qualified healthcare professional."
            ),
            (
                "Follow prescribed medication "
                "instructions and discuss any "
                "prescription warnings with a "
                "healthcare professional."
            ),
        ],
    }