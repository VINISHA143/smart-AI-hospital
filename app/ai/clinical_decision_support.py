from typing import List, Dict, Any


# ============================================================
# CLINICAL DECISION SUPPORT
# ============================================================
#
# This is a rule-based prototype.
# It is NOT a diagnostic system and must not replace
# professional clinical judgment.
# ============================================================


def normalize(value: str) -> str:
    """
    Normalize text for reliable rule matching.
    """
    return " ".join(
        str(value).lower().strip().split()
    )


def _normalize_list(values: List[str]) -> List[str]:
    """
    Normalize a list of text values and remove empty entries.
    """
    return [
        normalize(value)
        for value in values
        if value and str(value).strip()
    ]


def _extract_warning_count(
    prescription_analysis: Dict[str, Any],
) -> int:
    """
    Safely extract prescription warning count.
    """
    warnings = prescription_analysis.get("warnings", [])

    if isinstance(warnings, list):
        return len(warnings)

    return 0


def _get_triage_level(
    triage_analysis: Dict[str, Any],
) -> str:
    """
    Safely extract triage level.
    """
    return str(
        triage_analysis.get(
            "triage_level",
            "Unknown",
        )
    )


def _get_appointment_specialty(
    appointment_recommendation: Dict[str, Any],
) -> str:
    """
    Safely extract recommended specialty.
    """
    specialty = appointment_recommendation.get(
        "recommended_specialty"
    )

    if specialty:
        return str(specialty)

    department = appointment_recommendation.get(
        "recommended_department"
    )

    if department:
        return str(department)

    return "General Medicine"


def generate_clinical_decision_support(
    symptoms: List[str],
    diagnoses: List[str],
    medications: List[str],
    lab_findings: List[str],
    prescription_analysis: Dict[str, Any],
    triage_analysis: Dict[str, Any],
    appointment_recommendation: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate a structured clinical decision-support summary.

    Parameters
    ----------
    symptoms:
        Patient-reported symptoms.

    diagnoses:
        Existing or previously documented diagnoses.

    medications:
        Current or proposed medications.

    lab_findings:
        Relevant laboratory findings.

    prescription_analysis:
        Output from the prescription safety checker.

    triage_analysis:
        Output from the emergency triage engine.

    appointment_recommendation:
        Output from the appointment recommendation engine.

    Returns
    -------
    Dict[str, Any]
        Structured rule-based clinical decision-support result.
    """

    normalized_symptoms = _normalize_list(symptoms)
    normalized_diagnoses = _normalize_list(diagnoses)
    normalized_medications = _normalize_list(medications)
    normalized_lab_findings = _normalize_list(lab_findings)

    triage_level = _get_triage_level(
        triage_analysis
    )

    appointment_specialty = _get_appointment_specialty(
        appointment_recommendation
    )

    prescription_warning_count = _extract_warning_count(
        prescription_analysis
    )

    recommendations: List[str] = []
    alerts: List[str] = []
    clinical_factors: List[str] = []

    # ========================================================
    # 1. TRIAGE ASSESSMENT
    # ========================================================

    if triage_level == "Emergency":
        alerts.append(
            "Emergency indicators are present. "
            "Immediate professional medical assessment is required."
        )

        recommendations.append(
            "Prioritize emergency medical evaluation."
        )

    elif triage_level == "Urgent":
        alerts.append(
            "Urgent symptoms were identified by the triage analysis."
        )

        recommendations.append(
            "Arrange prompt medical evaluation."
        )

    elif triage_level == "Moderate":
        clinical_factors.append(
            "Moderate-level symptoms were identified."
        )

        recommendations.append(
            "Consider medical evaluation if symptoms persist "
            "or worsen."
        )

    elif triage_level == "Low":
        clinical_factors.append(
            "No high-priority emergency indicators were identified "
            "by the configured triage rules."
        )

    else:
        clinical_factors.append(
            "Triage information was not provided."
        )

    # ========================================================
    # 2. SYMPTOM ASSESSMENT
    # ========================================================

    if normalized_symptoms:
        clinical_factors.append(
            "Reported symptoms: "
            + ", ".join(normalized_symptoms)
            + "."
        )

    # ========================================================
    # 3. DIAGNOSIS CONTEXT
    # ========================================================

    if normalized_diagnoses:
        clinical_factors.append(
            "Existing diagnoses: "
            + ", ".join(normalized_diagnoses)
            + "."
        )

    # ========================================================
    # 4. MEDICATION CONTEXT
    # ========================================================

    if normalized_medications:
        clinical_factors.append(
            "Medications provided for review: "
            + ", ".join(normalized_medications)
            + "."
        )

    # ========================================================
    # 5. PRESCRIPTION SAFETY
    # ========================================================

    if prescription_warning_count > 0:
        alerts.append(
            f"{prescription_warning_count} prescription "
            "safety warning(s) were detected."
        )

        recommendations.append(
            "Review prescription safety findings with "
            "a qualified healthcare professional before "
            "making medication decisions."
        )

    else:
        clinical_factors.append(
            "No prescription warnings were supplied "
            "to the decision-support engine."
        )

    # ========================================================
    # 6. LAB FINDINGS
    # ========================================================

    if normalized_lab_findings:
        clinical_factors.append(
            "Laboratory findings provided: "
            + ", ".join(normalized_lab_findings)
            + "."
        )

        recommendations.append(
            "Interpret laboratory findings in the context "
            "of the patient's clinical history and "
            "laboratory-specific reference ranges."
        )

    # ========================================================
    # 7. APPOINTMENT RECOMMENDATION
    # ========================================================

    if appointment_recommendation:
        clinical_factors.append(
            "Recommended clinical specialty: "
            + appointment_specialty
            + "."
        )

        if triage_level not in {
            "Emergency",
            "Urgent",
        }:
            recommendations.append(
                "Follow the recommended clinical pathway "
                f"and consider evaluation by {appointment_specialty}."
            )

    # ========================================================
    # 8. GENERAL CLINICAL RULES
    # ========================================================

    symptom_set = set(normalized_symptoms)
    diagnosis_set = set(normalized_diagnoses)

    cardiovascular_indicators = {
        "chest pain",
        "severe chest pain",
        "palpitations",
        "shortness of breath",
        "high blood pressure",
    }

    respiratory_indicators = {
        "wheezing",
        "difficulty breathing",
        "shortness of breath",
        "chronic cough",
        "persistent cough",
    }

    neurological_indicators = {
        "sudden weakness",
        "sudden numbness",
        "difficulty speaking",
        "facial drooping",
        "seizure",
    }

    gastrointestinal_indicators = {
        "abdominal pain",
        "stomach pain",
        "persistent vomiting",
        "nausea",
        "diarrhea",
    }

    if symptom_set.intersection(
        cardiovascular_indicators
    ):
        clinical_factors.append(
            "Cardiovascular-related symptoms are present "
            "in the supplied information."
        )

    if symptom_set.intersection(
        respiratory_indicators
    ):
        clinical_factors.append(
            "Respiratory-related symptoms are present "
            "in the supplied information."
        )

    if symptom_set.intersection(
        neurological_indicators
    ):
        clinical_factors.append(
            "Neurological-related symptoms are present "
            "in the supplied information."
        )

    if symptom_set.intersection(
        gastrointestinal_indicators
    ):
        clinical_factors.append(
            "Gastrointestinal-related symptoms are present "
            "in the supplied information."
        )

    # ========================================================
    # 9. DIABETES / HYPERTENSION CONTEXT
    # ========================================================

    if "diabetes" in diagnosis_set:
        clinical_factors.append(
            "Diabetes is included in the supplied diagnosis context."
        )

    if "hypertension" in diagnosis_set:
        clinical_factors.append(
            "Hypertension is included in the supplied diagnosis context."
        )

    # ========================================================
    # 10. OVERALL PRIORITY
    # ========================================================

    if triage_level == "Emergency":
        overall_priority = "Emergency"

    elif triage_level == "Urgent":
        overall_priority = "High"

    elif prescription_warning_count > 0:
        overall_priority = "High"

    elif triage_level == "Moderate":
        overall_priority = "Moderate"

    else:
        overall_priority = "Routine"

    # ========================================================
    # 11. RECOMMENDED ACTION
    # ========================================================

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
            "symptoms persist, worsen, or new concerning symptoms "
            "develop."
        )

    else:
        recommended_action = (
            "Continue appropriate clinical monitoring and "
            "routine follow-up as determined by a healthcare "
            "professional."
        )

    # ========================================================
    # 12. FALLBACK RECOMMENDATION
    # ========================================================

    if not recommendations:
        recommendations.append(
            "Review the available clinical information with "
            "a qualified healthcare professional."
        )

    # Remove duplicate recommendations while preserving order.
    recommendations = list(
        dict.fromkeys(recommendations)
    )

    # Remove duplicate clinical factors.
    clinical_factors = list(
        dict.fromkeys(clinical_factors)
    )

    # Remove duplicate alerts.
    alerts = list(
        dict.fromkeys(alerts)
    )

    # ========================================================
    # 13. FINAL RESULT
    # ========================================================

    return {
        "success": True,
        "overall_priority": overall_priority,
        "triage_level": triage_level,
        "recommended_specialty": appointment_specialty,
        "symptoms": normalized_symptoms,
        "diagnoses": normalized_diagnoses,
        "medications": normalized_medications,
        "lab_findings": normalized_lab_findings,
        "clinical_factors": clinical_factors,
        "alerts": alerts,
        "recommendations": recommendations,
        "recommended_action": recommended_action,
        "prescription_warning_count": prescription_warning_count,
        "disclaimer": (
            "This clinical decision-support result is generated "
            "by a rule-based prototype for informational purposes "
            "only. It is not a diagnosis, does not prescribe "
            "treatment, and must not replace professional clinical "
            "judgment or emergency medical assessment."
        ),
    }