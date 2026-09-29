from typing import List, Dict


# ============================================================
# RISK FACTORS
# ============================================================

RISK_FACTORS: Dict[str, int] = {
    "chest pain": 25,
    "severe chest pain": 35,
    "shortness of breath": 25,
    "difficulty breathing": 35,
    "high blood pressure": 15,
    "high blood sugar": 15,
    "diabetes": 15,
    "obesity": 10,
    "smoking": 15,
    "high cholesterol": 10,
    "heart disease": 20,
    "fever": 5,
    "persistent vomiting": 10,
    "severe abdominal pain": 15,
    "fainting": 30,
    "seizure": 35,
    "sudden weakness": 30,
    "sudden numbness": 30,
    "difficulty speaking": 35,
}


# ============================================================
# EMERGENCY FACTORS
# ============================================================

EMERGENCY_FACTORS = {
    "severe chest pain",
    "difficulty breathing",
    "loss of consciousness",
    "fainting",
    "seizure",
    "sudden weakness",
    "sudden numbness",
    "difficulty speaking",
    "blue lips",
    "severe bleeding",
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(value: str) -> str:

    return " ".join(
        value.lower().strip().split()
    )


def normalize_list(
    values: List[str]
) -> set:

    return {
        normalize(item)
        for item in values
        if item and item.strip()
    }


# ============================================================
# HEALTH RISK CALCULATOR
#
# This version supports BOTH:
#
# 1. The old 4-argument AI engine format
# 2. The 9-argument format used by app/api/ai.py
# ============================================================

def calculate_health_risk(
    age: int,
    symptoms: List[str] = None,
    conditions: List[str] = None,
    risk_factors: List[str] = None,
    bmi: float = 0,
    blood_pressure: str = "",
    glucose: float = 0,
    cholesterol: float = 0,
    smoking: bool = False,
    diabetes: bool = False,
    hypertension: bool = False,
    heart_disease: bool = False,
) -> Dict:

    # --------------------------------------------------------
    # Safe defaults
    # --------------------------------------------------------

    symptoms = symptoms or []
    conditions = conditions or []
    risk_factors = risk_factors or []

    # --------------------------------------------------------
    # Normalize input
    # --------------------------------------------------------

    normalized_symptoms = normalize_list(
        symptoms
    )

    normalized_conditions = normalize_list(
        conditions
    )

    normalized_risk_factors = normalize_list(
        risk_factors
    )

    all_factors = (
        normalized_symptoms
        | normalized_conditions
        | normalized_risk_factors
    )

    # --------------------------------------------------------
    # Add structured boolean inputs
    # --------------------------------------------------------

    if smoking:
        all_factors.add("smoking")

    if diabetes:
        all_factors.add("diabetes")

    if hypertension:
        all_factors.add(
            "high blood pressure"
        )

    if heart_disease:
        all_factors.add(
            "heart disease"
        )

    # --------------------------------------------------------
    # BMI
    # --------------------------------------------------------

    if bmi >= 30:
        all_factors.add("obesity")

    # --------------------------------------------------------
    # Blood pressure
    # --------------------------------------------------------

    if blood_pressure:

        try:

            parts = blood_pressure.split("/")

            systolic = float(parts[0])
            diastolic = float(parts[1])

            if (
                systolic >= 140
                or diastolic >= 90
            ):
                all_factors.add(
                    "high blood pressure"
                )

        except (
            ValueError,
            IndexError
        ):
            pass

    # --------------------------------------------------------
    # Glucose
    # --------------------------------------------------------

    if glucose >= 126:
        all_factors.add(
            "high blood sugar"
        )

    # --------------------------------------------------------
    # Cholesterol
    # --------------------------------------------------------

    if cholesterol >= 200:
        all_factors.add(
            "high cholesterol"
        )

    # --------------------------------------------------------
    # Calculate score
    # --------------------------------------------------------

    score = 0
    matched_factors = []

    for factor, weight in RISK_FACTORS.items():

        if factor in all_factors:

            score += weight

            matched_factors.append({
                "factor": factor,
                "weight": weight,
            })

    # --------------------------------------------------------
    # Age contribution
    # --------------------------------------------------------

    age_points = 0

    if age >= 65:

        age_points = 15

    elif age >= 50:

        age_points = 10

    elif age >= 40:

        age_points = 5

    if age_points > 0:

        score += age_points

        matched_factors.append({
            "factor": f"age {age}",
            "weight": age_points,
        })

    # --------------------------------------------------------
    # Limit score
    # --------------------------------------------------------

    score = min(score, 100)

    # --------------------------------------------------------
    # Emergency detection
    # --------------------------------------------------------

    emergency_matches = sorted(
        normalized_symptoms.intersection(
            EMERGENCY_FACTORS
        )
    )

    # --------------------------------------------------------
    # Risk level
    # --------------------------------------------------------

    if emergency_matches:

        risk_level = "Critical"

    elif score >= 60:

        risk_level = "High"

    elif score >= 30:

        risk_level = "Moderate"

    elif score > 0:

        risk_level = "Low"

    else:

        risk_level = "Minimal"

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    if risk_level == "Critical":

        recommendation = (
            "Immediate emergency medical assessment "
            "is recommended."
        )

    elif risk_level == "High":

        recommendation = (
            "Prompt medical evaluation is recommended. "
            "A qualified healthcare professional should "
            "review the patient's risk factors."
        )

    elif risk_level == "Moderate":

        recommendation = (
            "Medical evaluation and appropriate follow-up "
            "are recommended, particularly if symptoms "
            "persist or worsen."
        )

    elif risk_level == "Low":

        recommendation = (
            "Routine monitoring and appropriate medical "
            "follow-up are recommended."
        )

    else:

        recommendation = (
            "No significant risk factors were detected "
            "by the configured prototype rules."
        )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {
        "success": True,
        "risk_score": score,
        "risk_level": risk_level,
        "age": age,
        "matched_factors": matched_factors,
        "emergency_indicators": emergency_matches,
        "recommendation": recommendation,
        "disclaimer": (
            "This health risk score is an informational "
            "prototype. It is not a diagnosis, medical "
            "prediction, or substitute for evaluation by "
            "a qualified healthcare professional."
        ),
    }