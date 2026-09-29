from typing import Dict


def calculate_patient_flow(
    current_patients: int,
    average_daily_patients: float,
    current_admissions: int,
    average_daily_admissions: float,
    current_discharges: int,
    average_daily_discharges: float,
    current_emergency_cases: int,
    average_daily_emergency_cases: float,
    total_beds: int,
    occupied_beds: int,
    prediction_days: int,
) -> Dict:

    # Current bed occupancy
    occupancy_percentage = round(
        (occupied_beds / total_beds) * 100,
        2
    )

    # Daily patient flow balance
    daily_net_change = round(
        average_daily_admissions - average_daily_discharges,
        2
    )

    # Projected patient count
    projected_patients = round(
        current_patients + (
            daily_net_change * prediction_days
        ),
        2
    )

    # Projected admissions and discharges
    projected_admissions = round(
        average_daily_admissions * prediction_days,
        2
    )

    projected_discharges = round(
        average_daily_discharges * prediction_days,
        2
    )

    # Projected emergency cases
    projected_emergency_cases = round(
        average_daily_emergency_cases * prediction_days,
        2
    )

    # Projected occupied beds
    projected_occupied_beds = round(
        occupied_beds + (
            daily_net_change * prediction_days
        ),
        2
    )

    projected_occupancy = round(
        (projected_occupied_beds / total_beds) * 100,
        2
    )

    risk_factors = []

    if occupancy_percentage >= 90:
        risk_factors.append("Current bed occupancy is very high")
    elif occupancy_percentage >= 80:
        risk_factors.append("Current bed occupancy is high")

    if projected_occupancy >= 90:
        risk_factors.append(
            "Projected bed occupancy is very high"
        )
    elif projected_occupancy >= 80:
        risk_factors.append(
            "Projected bed occupancy is high"
        )

    if daily_net_change > 0:
        risk_factors.append(
            "Admissions are currently exceeding discharges"
        )
    elif daily_net_change < 0:
        risk_factors.append(
            "Discharges are currently exceeding admissions"
        )

    if average_daily_emergency_cases > 0:
        emergency_ratio = (
            average_daily_emergency_cases /
            max(average_daily_patients, 1)
        )

        if emergency_ratio >= 0.20:
            risk_factors.append(
                "High proportion of emergency cases"
            )

    # Determine flow level
    if projected_occupancy >= 95 or (
        daily_net_change > 0 and
        projected_occupancy >= 90
    ):
        flow_level = "Critical"
        recommendation = (
            "Hospital patient flow pressure is projected to be critical. "
            "Review bed availability, admissions, discharges and emergency "
            "capacity promptly."
        )

    elif projected_occupancy >= 80 or len(risk_factors) >= 3:
        flow_level = "High"
        recommendation = (
            "High patient-flow pressure is projected. "
            "Monitor bed capacity and admission/discharge trends closely."
        )

    elif len(risk_factors) >= 1:
        flow_level = "Moderate"
        recommendation = (
            "Moderate patient-flow pressure detected. "
            "Continue monitoring patient volume and hospital resources."
        )

    else:
        flow_level = "Normal"
        recommendation = (
            "Patient-flow indicators are within the configured "
            "prototype monitoring thresholds."
        )

    return {
        "success": True,
        "flow_level": flow_level,

        "current_status": {
            "current_patients": current_patients,
            "current_admissions": current_admissions,
            "current_discharges": current_discharges,
            "current_emergency_cases": current_emergency_cases,
            "occupied_beds": occupied_beds,
            "total_beds": total_beds,
            "occupancy_percentage": occupancy_percentage,
        },

        "daily_flow": {
            "average_daily_patients": average_daily_patients,
            "average_daily_admissions": average_daily_admissions,
            "average_daily_discharges": average_daily_discharges,
            "average_daily_emergency_cases": (
                average_daily_emergency_cases
            ),
            "daily_net_change": daily_net_change,
        },

        "prediction": {
            "prediction_days": prediction_days,
            "projected_patients": projected_patients,
            "projected_admissions": projected_admissions,
            "projected_discharges": projected_discharges,
            "projected_emergency_cases": projected_emergency_cases,
            "projected_occupied_beds": projected_occupied_beds,
            "projected_occupancy_percentage": projected_occupancy,
        },

        "risk_factors": risk_factors,

        "recommendation": recommendation,

        "disclaimer": (
            "This hospital patient-flow prediction is a rule-based "
            "prototype for informational and operational planning "
            "purposes only. It is not a validated forecasting model "
            "and should not replace hospital operational judgment."
        ),
    }