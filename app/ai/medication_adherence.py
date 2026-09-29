from typing import Dict, List


def calculate_medication_adherence_risk(
    missed_doses: int,
    total_doses: int,
    previous_non_adherence: int,
    side_effects: List[str],
    cost_problem: bool,
    forgetfulness: bool,
) -> Dict:

    # Calculate adherence percentage
    if total_doses > 0:
        taken_doses = max(total_doses - missed_doses, 0)
        adherence_percentage = round(
            (taken_doses / total_doses) * 100,
            2
        )
    else:
        adherence_percentage = 0.0

    score = 0
    risk_factors = []

    # Missed-dose risk
    if total_doses > 0:
        missed_rate = missed_doses / total_doses

        if missed_rate >= 0.30:
            score += 40
            risk_factors.append("High proportion of missed doses")
        elif missed_rate >= 0.15:
            score += 25
            risk_factors.append("Moderate proportion of missed doses")
        elif missed_rate > 0:
            score += 10
            risk_factors.append("Some doses have been missed")

    # Previous non-adherence
    if previous_non_adherence >= 3:
        score += 25
        risk_factors.append("History of repeated medication non-adherence")
    elif previous_non_adherence > 0:
        score += 15
        risk_factors.append("Previous medication non-adherence")

    # Side effects
    if side_effects:
        score += 15
        risk_factors.append("Medication side effects reported")

    # Cost problem
    if cost_problem:
        score += 10
        risk_factors.append("Medication cost problem reported")

    # Forgetfulness
    if forgetfulness:
        score += 15
        risk_factors.append("Forgetfulness reported as a barrier")

    score = min(score, 100)

    # Determine risk level
    if score >= 60:
        risk_level = "High"
        recommendation = (
            "High medication adherence risk detected. "
            "Clinical review and discussion of adherence barriers "
            "are recommended."
        )
    elif score >= 30:
        risk_level = "Moderate"
        recommendation = (
            "Moderate medication adherence risk detected. "
            "Continue monitoring and address identified adherence barriers."
        )
    elif score > 0:
        risk_level = "Low"
        recommendation = (
            "Some medication adherence risk factors were identified. "
            "Continue monitoring and reinforce the prescribed medication plan."
        )
    else:
        risk_level = "Minimal"
        recommendation = (
            "No significant medication adherence risk factors were "
            "identified using the configured prototype rules."
        )

    # Practical recommendations
    adherence_support = []

    if forgetfulness:
        adherence_support.append(
            "Consider reminders or a consistent medication routine."
        )

    if side_effects:
        adherence_support.append(
            "Discuss reported medication side effects with a "
            "qualified healthcare professional."
        )

    if cost_problem:
        adherence_support.append(
            "Discuss medication affordability options with a "
            "qualified healthcare professional or pharmacist."
        )

    if missed_doses > 0:
        adherence_support.append(
            "Review the reasons for missed doses with the healthcare team."
        )

    if not adherence_support:
        adherence_support.append(
            "Continue taking medications only as prescribed."
        )

    return {
        "success": True,
        "adherence_percentage": adherence_percentage,
        "missed_doses": missed_doses,
        "total_doses": total_doses,
        "adherence_risk_score": score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "adherence_support": adherence_support,
        "recommendation": recommendation,
        "disclaimer": (
            "This medication adherence assessment is a rule-based "
            "prototype for informational purposes only. It does not "
            "replace medication counseling, clinical assessment, or "
            "professional healthcare advice."
        ),
    }