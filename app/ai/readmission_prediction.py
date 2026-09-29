from typing import Dict, List


READMISSION_RISK_FACTORS: Dict[str, int] = {
    "previous admission": 15,
    "multiple admissions": 20,
    "previous readmission": 20,
    "chronic disease": 15,
    "diabetes": 10,
    "hypertension": 10,
    "heart disease": 15,
    "kidney disease": 15,
    "copd": 15,
    "asthma": 10,
    "emergency admission": 15,
    "long hospital stay": 10,
}


def normalize(value: str) -> str:
    return " ".join(
        value.lower().strip().split()
    )


def calculate_readmission_risk(
    age: int,
    previous_admissions: int,
    previous_readmissions: int,
    chronic_conditions: List[str],
    length_of_stay: int,
    emergency_admission: bool,
) -> Dict:

    normalized_conditions = {
        normalize(condition)
        for condition in chronic_conditions
        if condition and condition.strip()
    }

    score = 0
    matched_factors = []

    # ---------------------------------------------------------
    # PREVIOUS ADMISSIONS
    # ---------------------------------------------------------

    if previous_admissions >= 3:
        weight = READMISSION_RISK_FACTORS[
            "multiple admissions"
        ]

        score += weight

        matched_factors.append({
            "factor": "multiple admissions",
            "weight": weight,
        })

    elif previous_admissions >= 1:
        weight = READMISSION_RISK_FACTORS[
            "previous admission"
        ]

        score += weight

        matched_factors.append({
            "factor": "previous admission",
            "weight": weight,
        })

    # ---------------------------------------------------------
    # PREVIOUS READMISSIONS
    # ---------------------------------------------------------

    if previous_readmissions >= 2:
        weight = READMISSION_RISK_FACTORS[
            "previous readmission"
        ]

        score += weight

        matched_factors.append({
            "factor": "multiple previous readmissions",
            "weight": weight,
        })

    elif previous_readmissions == 1:
        score += 10

        matched_factors.append({
            "factor": "previous readmission",
            "weight": 10,
        })

    # ---------------------------------------------------------
    # AGE
    # ---------------------------------------------------------

    if age >= 75:
        score += 15

        matched_factors.append({
            "factor": f"age {age}",
            "weight": 15,
        })

    elif age >= 65:
        score += 10

        matched_factors.append({
            "factor": f"age {age}",
            "weight": 10,
        })

    elif age >= 50:
        score += 5

        matched_factors.append({
            "factor": f"age {age}",
            "weight": 5,
        })

    # ---------------------------------------------------------
    # LENGTH OF STAY
    # ---------------------------------------------------------

    if length_of_stay >= 14:
        score += 15

        matched_factors.append({
            "factor": "prolonged hospital stay",
            "weight": 15,
        })

    elif length_of_stay >= 7:
        weight = READMISSION_RISK_FACTORS[
            "long hospital stay"
        ]

        score += weight

        matched_factors.append({
            "factor": "long hospital stay",
            "weight": weight,
        })

    # ---------------------------------------------------------
    # CHRONIC CONDITIONS
    # ---------------------------------------------------------

    chronic_condition_weights = {
        "chronic disease": 15,
        "diabetes": 10,
        "hypertension": 10,
        "heart disease": 15,
        "kidney disease": 15,
        "copd": 15,
        "asthma": 10,
    }

    for condition, weight in chronic_condition_weights.items():

        if condition in normalized_conditions:

            score += weight

            matched_factors.append({
                "factor": condition,
                "weight": weight,
            })

    # ---------------------------------------------------------
    # EMERGENCY ADMISSION
    # ---------------------------------------------------------

    if emergency_admission:

        weight = READMISSION_RISK_FACTORS[
            "emergency admission"
        ]

        score += weight

        matched_factors.append({
            "factor": "emergency admission",
            "weight": weight,
        })

    # ---------------------------------------------------------
    # LIMIT SCORE
    # ---------------------------------------------------------

    score = min(score, 100)

    # ---------------------------------------------------------
    # RISK LEVEL
    # ---------------------------------------------------------

    if score >= 60:
        risk_level = "High"

    elif score >= 30:
        risk_level = "Moderate"

    elif score > 0:
        risk_level = "Low"

    else:
        risk_level = "Minimal"

    # ---------------------------------------------------------
    # RECOMMENDATION
    # ---------------------------------------------------------

    if risk_level == "High":

        recommendation = (
            "Higher readmission risk indicators were detected. "
            "Consider enhanced discharge planning, follow-up, "
            "medication review, and appropriate post-discharge care."
        )

    elif risk_level == "Moderate":

        recommendation = (
            "Moderate readmission risk indicators were detected. "
            "Consider appropriate follow-up and discharge planning."
        )

    elif risk_level == "Low":

        recommendation = (
            "Some readmission risk factors were detected. "
            "Routine follow-up and monitoring are recommended."
        )

    else:

        recommendation = (
            "No significant readmission risk indicators were "
            "detected by the configured prototype rules."
        )

    return {
        "success": True,
        "readmission_risk_score": score,
        "readmission_risk_level": risk_level,
        "patient_age": age,
        "previous_admissions": previous_admissions,
        "previous_readmissions": previous_readmissions,
        "length_of_stay": length_of_stay,
        "emergency_admission": emergency_admission,
        "chronic_conditions": sorted(
            normalized_conditions
        ),
        "matched_risk_factors": matched_factors,
        "recommendation": recommendation,
        "disclaimer": (
            "This readmission risk prediction is an informational "
            "prototype based on supplied patient information. "
            "It is not a validated clinical prediction model and "
            "must not replace professional clinical judgment."
        ),
    }