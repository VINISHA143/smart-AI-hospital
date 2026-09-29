from typing import Dict


def predict_hospital_resources(
    current_patients: int,
    average_daily_admissions: float,
    average_daily_discharges: float,
    total_beds: int,
    occupied_beds: int,
    prediction_days: int,
) -> Dict:

    # Calculate daily net patient change
    daily_net_change = (
        average_daily_admissions
        - average_daily_discharges
    )

    # Predict patient count
    predicted_patients = (
        current_patients
        + (daily_net_change * prediction_days)
    )

    predicted_patients = max(
        0,
        round(predicted_patients, 2)
    )

    # Predict occupied beds
    predicted_occupied_beds = min(
        total_beds,
        max(0, round(predicted_patients))
    )

    predicted_available_beds = max(
        0,
        total_beds - predicted_occupied_beds
    )

    # Current occupancy
    if total_beds > 0:
        current_occupancy_rate = round(
            (occupied_beds / total_beds) * 100,
            2
        )
    else:
        current_occupancy_rate = 0

    # Predicted occupancy
    if total_beds > 0:
        predicted_occupancy_rate = round(
            (predicted_occupied_beds / total_beds) * 100,
            2
        )
    else:
        predicted_occupancy_rate = 0

    # Demand status
    if predicted_occupied_beds >= total_beds:
        demand_status = "Critical"
    elif predicted_occupancy_rate >= 80:
        demand_status = "High"
    elif predicted_occupancy_rate >= 60:
        demand_status = "Moderate"
    else:
        demand_status = "Low"

    observations = [
        f"Current patient count is {current_patients}.",
        (
            f"Average daily admissions are "
            f"{average_daily_admissions}."
        ),
        (
            f"Average daily discharges are "
            f"{average_daily_discharges}."
        ),
        (
            f"Predicted patient count after "
            f"{prediction_days} day(s) is "
            f"{predicted_patients}."
        ),
        (
            f"Predicted bed occupancy is "
            f"{predicted_occupancy_rate}%."
        ),
    ]

    recommendations = []

    if demand_status == "Critical":
        recommendations.append(
            "Projected demand may exceed available bed capacity. "
            "Review bed allocation and admission planning."
        )
    elif demand_status == "High":
        recommendations.append(
            "Monitor bed utilization closely and prepare "
            "for increased resource demand."
        )
    elif demand_status == "Moderate":
        recommendations.append(
            "Continue monitoring admissions, discharges, "
            "and bed utilization."
        )
    else:
        recommendations.append(
            "Current projected capacity appears to have "
            "available bed space."
        )

    if daily_net_change > 0:
        recommendations.append(
            "Patient volume is projected to increase based "
            "on the supplied admission and discharge averages."
        )
    elif daily_net_change < 0:
        recommendations.append(
            "Patient volume is projected to decrease based "
            "on the supplied admission and discharge averages."
        )
    else:
        recommendations.append(
            "Patient volume is projected to remain approximately stable."
        )

    return {
        "success": True,
        "input_summary": {
            "current_patients": current_patients,
            "average_daily_admissions": average_daily_admissions,
            "average_daily_discharges": average_daily_discharges,
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "prediction_days": prediction_days,
        },
        "current_status": {
            "occupied_beds": occupied_beds,
            "available_beds": max(
                0,
                total_beds - occupied_beds
            ),
            "occupancy_rate": current_occupancy_rate,
        },
        "prediction": {
            "predicted_patients": predicted_patients,
            "predicted_occupied_beds": predicted_occupied_beds,
            "predicted_available_beds": predicted_available_beds,
            "predicted_occupancy_rate": predicted_occupancy_rate,
            "daily_net_patient_change": round(
                daily_net_change,
                2
            ),
            "prediction_days": prediction_days,
        },
        "demand_status": demand_status,
        "observations": observations,
        "recommendations": recommendations,
        "disclaimer": (
            "This resource prediction is a rule-based operational "
            "prototype for informational purposes only. It should "
            "not replace hospital management decisions or "
            "professional clinical judgment."
        ),
    }