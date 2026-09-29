from typing import Dict, List


DISCHARGE_RISK_WEIGHTS: Dict[str, int] = {
    "older age": 10,
    "very old age": 15,
    "long hospital stay": 10,
    "very long hospital stay": 15,
    "chronic condition": 10,
    "multiple chronic conditions": 20,
    "abnormal lab result": 15,
    "multiple abnormal lab results": 25,
    "mobility problem": 20,
    "limited social support": 20,
}


def normalize(value: str) -> str:
    return " ".join(
        value.lower().strip().split()
    )


def calculate_discharge_risk(
    age: int,
    length_of_stay: int,
    chronic_conditions: List[str],
    abnormal_lab_results: List[str],
    mobility_problem: bool,
    social_support: str,
) -> Dict:

    score = 0
    matched_factors = []

    normalized_conditions = {
        normalize(condition)
        for condition in chronic_conditions
        if condition and condition.strip()
    }

    normalized_labs = [
        normalize(result)
        for result in abnormal_lab_results
        if result and result.strip()
    ]

    normalized_social_support = normalize(
        social_support
    )

    # ========================================================
    # AGE
    # ========================================================

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

    # ========================================================
    # LENGTH OF STAY
    # ========================================================

    if length_of_stay >= 14:
        score += 15

        matched_factors.append({
            "factor": "very long hospital stay",
            "weight": 15,
        })

    elif length_of_stay >= 7:
        score += 10

        matched_factors.append({
            "factor": "long hospital stay",
            "weight": 10,
        })

    # ========================================================
    # CHRONIC CONDITIONS
    # ========================================================

    if len(normalized_conditions) >= 3:
        score += 20

        matched_factors.append({
            "factor": "multiple chronic conditions",
            "weight": 20,
        })

    elif len(normalized_conditions) >= 1:
        score += 10

        matched_factors.append({
            "factor": "chronic medical condition",
            "weight": 10,
        })

    # ========================================================
    # ABNORMAL LAB RESULTS
    # ========================================================

    if len(normalized_labs) >= 3:
        score += 25

        matched_factors.append({
            "factor": "multiple abnormal lab results",
            "weight": 25,
        })

    elif len(normalized_labs) >= 1:
        score += 15

        matched_factors.append({
            "factor": "abnormal lab result",
            "weight": 15,
        })

    # ========================================================
    # MOBILITY PROBLEM
    # ========================================================

    if mobility_problem:
        score += 20

        matched_factors.append({
            "factor": "mobility problem",
            "weight": 20,
        })

    # ========================================================
    # SOCIAL SUPPORT
    # ========================================================

    if normalized_social_support in {
        "poor",
        "limited",
        "inadequate",
        "none",
    }:
        score += 20

        matched_factors.append({
            "factor": "limited social support",
            "weight": 20,
        })

    # ========================================================
    # LIMIT SCORE
    # ========================================================

    score = min(score, 100)

    # ========================================================
    # RISK LEVEL
    # ========================================================

    if score >= 60:
        risk_level = "High"

    elif score >= 30:
        risk_level = "Moderate"

    elif score > 0:
        risk_level = "Low"

    else:
        risk_level = "Minimal"

    # ========================================================
    # FOLLOW-UP PRIORITY
    # ========================================================

    if risk_level == "High":
        follow_up_priority = "Immediate"

    elif risk_level == "Moderate":
        follow_up_priority = "Priority"

    else:
        follow_up_priority = "Routine"

    # ========================================================
    # DISCHARGE STATUS
    # ========================================================

    if risk_level == "High":
        discharge_status = "Needs Clinical Review"

    elif risk_level == "Moderate":
        discharge_status = "Review Before Discharge"

    else:
        discharge_status = "Routine Review"

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    recommendations = []

    if normalized_labs:
        recommendations.append(
            "Review abnormal laboratory results "
            "before discharge."
        )

    if mobility_problem:
        recommendations.append(
            "Assess mobility needs and consider appropriate "
            "support or rehabilitation planning."
        )

    if normalized_social_support in {
        "poor",
        "limited",
        "inadequate",
        "none",
    }:
        recommendations.append(
            "Review available social and home support "
            "before discharge."
        )

    if len(normalized_conditions) >= 2:
        recommendations.append(
            "Ensure chronic disease management and "
            "follow-up planning are documented."
        )

    if length_of_stay >= 7:
        recommendations.append(
            "Review discharge readiness and continuity "
            "of care after a prolonged hospitalization."
        )

    if age >= 65:
        recommendations.append(
            "Consider additional discharge support "
            "and follow-up for an older patient."
        )

    if not recommendations:
        recommendations.append(
            "Continue routine discharge planning and "
            "follow-up according to clinical requirements."
        )

    # ========================================================
    # FOLLOW-UP PLAN
    # ========================================================

    if follow_up_priority == "Immediate":
        follow_up_plan = (
            "Arrange prompt post-discharge clinical follow-up "
            "and review all identified discharge risk factors."
        )

    elif follow_up_priority == "Priority":
        follow_up_plan = (
            "Arrange timely post-discharge follow-up and "
            "monitor unresolved discharge concerns."
        )

    else:
        follow_up_plan = (
            "Routine post-discharge follow-up should be "
            "arranged according to the patient's clinical needs."
        )

    # ========================================================
    # RESULT
    # ========================================================

    return {
        "success": True,
        "discharge_risk_score": score,
        "discharge_risk_level": risk_level,
        "discharge_status": discharge_status,
        "follow_up_priority": follow_up_priority,

        "patient_information": {
            "age": age,
            "length_of_stay": length_of_stay,
            "chronic_condition_count": len(
                normalized_conditions
            ),
            "chronic_conditions": sorted(
                normalized_conditions
            ),
            "abnormal_lab_result_count": len(
                normalized_labs
            ),
            "abnormal_lab_results": normalized_labs,
            "mobility_problem": mobility_problem,
            "social_support": normalized_social_support,
        },

        "matched_risk_factors": matched_factors,

        "follow_up_plan": follow_up_plan,

        "recommendations": recommendations,

        "disclaimer": (
            "This discharge risk assessment is an informational "
            "prototype based on supplied patient information. "
            "It is not a validated clinical prediction model "
            "and must not replace professional clinical judgment."
        ),
    }