from typing import Any, Dict, List


def generate_patient_summary(
    symptoms: List[str],
    disease_risk: Dict[str, Any],
    medical_report: Dict[str, Any],
    prescription_analysis: Dict[str, Any],
    triage_analysis: Dict[str, Any],
    appointment_recommendation: Dict[str, Any],
) -> Dict[str, Any]:

    # ---------------------------------------------------------
    # SAFE INPUT NORMALIZATION
    # ---------------------------------------------------------

    if not isinstance(symptoms, list):
        symptoms = []

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
    # CLEAN SYMPTOMS
    # ---------------------------------------------------------

    clean_symptoms = []

    for symptom in symptoms:
        if symptom is None:
            continue

        text = str(symptom).strip()

        if text:
            clean_symptoms.append(text)

    # ---------------------------------------------------------
    # HEALTH RISK
    # ---------------------------------------------------------

    health_risk_score = disease_risk.get(
        "risk_score",
        disease_risk.get("score", 0),
    )

    health_risk_level = disease_risk.get(
        "risk_level",
        disease_risk.get("level", "Unknown"),
    )

    if health_risk_level is None:
        health_risk_level = "Unknown"

    health_risk_level = str(health_risk_level)

    # ---------------------------------------------------------
    # TRIAGE
    # ---------------------------------------------------------

    triage_level = triage_analysis.get(
        "triage_level",
        triage_analysis.get("level", "Unknown"),
    )

    if triage_level is None:
        triage_level = "Unknown"

    triage_level = str(triage_level)

    # ---------------------------------------------------------
    # PRESCRIPTION SAFETY
    # ---------------------------------------------------------

    prescription_safety = prescription_analysis.get(
        "safety_level",
        prescription_analysis.get("level", "Unknown"),
    )

    if prescription_safety is None:
        prescription_safety = "Unknown"

    prescription_safety = str(prescription_safety)

    prescription_warnings = prescription_analysis.get(
        "warnings",
        [],
    )

    if not isinstance(prescription_warnings, list):
        prescription_warnings = []

    # ---------------------------------------------------------
    # MEDICAL REPORT
    # ---------------------------------------------------------

    report_severity = medical_report.get(
        "severity",
        "Unknown",
    )

    if report_severity is None:
        report_severity = "Unknown"

    report_severity = str(report_severity)

    abnormal_parameters = medical_report.get(
        "abnormal_parameters",
        [],
    )

    if not isinstance(abnormal_parameters, list):
        abnormal_parameters = []

    # IMPORTANT:
    # Never allow None to reach ", ".join()
    abnormal_parameter_names = []

    for item in abnormal_parameters:

        if isinstance(item, dict):

            parameter = item.get("parameter")

            if parameter is not None:
                parameter = str(parameter).strip()

                if parameter:
                    abnormal_parameter_names.append(parameter)

        elif isinstance(item, str):

            item = item.strip()

            if item:
                abnormal_parameter_names.append(item)

        elif item is not None:

            text = str(item).strip()

            if text:
                abnormal_parameter_names.append(text)

    # ---------------------------------------------------------
    # DETERMINE OVERALL PRIORITY
    # ---------------------------------------------------------

    if triage_level.lower() == "emergency":

        overall_priority = "Emergency"

    elif (
        health_risk_level.lower() == "critical"
        or prescription_safety.lower() == "high"
        or report_severity.lower() == "high"
    ):

        overall_priority = "High"

    elif (
        health_risk_level.lower() == "high"
        or prescription_safety.lower() == "moderate"
        or report_severity.lower() == "moderate"
        or triage_level.lower() == "urgent"
    ):

        overall_priority = "Moderate"

    else:

        overall_priority = "Routine"

    # ---------------------------------------------------------
    # BUILD SUMMARY
    # ---------------------------------------------------------

    summary_parts = []

    if clean_symptoms:

        summary_parts.append(
            "Reported symptoms: "
            + ", ".join(clean_symptoms)
            + "."
        )

    if abnormal_parameter_names:

        summary_parts.append(
            "Abnormal medical report parameters: "
            + ", ".join(abnormal_parameter_names)
            + "."
        )

    if prescription_warnings:

        summary_parts.append(
            f"{len(prescription_warnings)} "
            "prescription safety warning(s) detected."
        )

    if triage_level != "Unknown":

        summary_parts.append(
            f"Emergency triage level: {triage_level}."
        )

    if health_risk_level != "Unknown":

        summary_parts.append(
            f"Health risk level: {health_risk_level}."
        )

    summary = " ".join(summary_parts)

    if not summary:

        summary = (
            "Insufficient clinical information was provided "
            "to generate a detailed summary."
        )

    # ---------------------------------------------------------
    # RECOMMENDED ACTION
    # ---------------------------------------------------------

    if overall_priority == "Emergency":

        recommended_action = (
            "Immediate emergency medical assessment is recommended."
        )

    elif overall_priority == "High":

        recommended_action = (
            "Prompt review by a qualified healthcare professional "
            "is recommended."
        )

    elif overall_priority == "Moderate":

        recommended_action = (
            "Medical follow-up is recommended, particularly if "
            "symptoms or abnormalities persist or worsen."
        )

    else:

        recommended_action = (
            "Continue routine monitoring and follow-up "
            "as clinically appropriate."
        )

    # ---------------------------------------------------------
    # APPOINTMENT
    # ---------------------------------------------------------

    recommended_department = appointment_recommendation.get(
        "recommended_department"
    )

    recommended_specialty = appointment_recommendation.get(
        "recommended_specialty"
    )

    # ---------------------------------------------------------
    # FINAL RESPONSE
    # ---------------------------------------------------------

    return {
        "success": True,

        "overall_priority": overall_priority,

        "summary": summary,

        "reported_symptoms": clean_symptoms,

        "health_risk": {
            "score": health_risk_score,
            "level": health_risk_level,
        },

        "medical_report": {
            "severity": report_severity,
            "abnormal_parameters": abnormal_parameter_names,
        },

        "prescription_safety": {
            "level": prescription_safety,
            "warning_count": len(
                prescription_warnings
            ),
        },

        "emergency_triage": {
            "level": triage_level,
        },

        "appointment": {
            "department": recommended_department,
            "specialty": recommended_specialty,
        },

        "recommended_action": recommended_action,

        "disclaimer": (
            "This patient summary is an informational prototype. "
            "It is not a medical diagnosis and must not replace "
            "professional clinical assessment or judgment."
        ),
    }