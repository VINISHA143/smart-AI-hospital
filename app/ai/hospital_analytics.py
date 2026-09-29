from typing import Dict


def _safe_percentage(value: float, total: float) -> float:
    """
    Calculate a percentage safely.

    Returns 0.0 when the denominator is zero.
    """
    if total <= 0:
        return 0.0

    return round((value / total) * 100, 2)


def calculate_hospital_analytics(
    total_patients: int,
    total_doctors: int,
    total_appointments: int,
    total_admissions: int,
    total_discharges: int,
    total_emergency_cases: int,
    total_beds: int,
    occupied_beds: int,
) -> Dict:
    """
    Calculate hospital-level operational analytics.

    This is a rule-based analytics prototype.
    It does not provide clinical diagnosis or treatment advice.
    """

    # ------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------

    values = {
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "total_admissions": total_admissions,
        "total_discharges": total_discharges,
        "total_emergency_cases": total_emergency_cases,
        "total_beds": total_beds,
        "occupied_beds": occupied_beds,
    }

    for name, value in values.items():
        if value < 0:
            raise ValueError(
                f"{name} cannot be negative."
            )

    if occupied_beds > total_beds:
        raise ValueError(
            "occupied_beds cannot be greater than total_beds."
        )

    if total_discharges > total_admissions:
        discharge_note = (
            "Discharges exceed admissions in the supplied "
            "reporting data. Verify the reporting period."
        )
    else:
        discharge_note = (
            "Discharge volume is within the supplied "
            "admission count."
        )

    # ------------------------------------------------------------
    # CALCULATE BED METRICS
    # ------------------------------------------------------------

    available_beds = total_beds - occupied_beds

    bed_occupancy_rate = _safe_percentage(
        occupied_beds,
        total_beds,
    )

    bed_availability_rate = _safe_percentage(
        available_beds,
        total_beds,
    )

    # ------------------------------------------------------------
    # CALCULATE PATIENT / DOCTOR METRICS
    # ------------------------------------------------------------

    patients_per_doctor = (
        round(total_patients / total_doctors, 2)
        if total_doctors > 0
        else 0.0
    )

    appointments_per_patient = (
        round(total_appointments / total_patients, 2)
        if total_patients > 0
        else 0.0
    )

    admissions_per_patient = _safe_percentage(
        total_admissions,
        total_patients,
    )

    discharges_per_admission = _safe_percentage(
        total_discharges,
        total_admissions,
    )

    emergency_case_rate = _safe_percentage(
        total_emergency_cases,
        total_patients,
    )

    # ------------------------------------------------------------
    # OPERATIONAL STATUS
    # ------------------------------------------------------------

    if total_beds == 0:
        bed_status = "No beds configured"
    elif bed_occupancy_rate >= 90:
        bed_status = "Very High Occupancy"
    elif bed_occupancy_rate >= 75:
        bed_status = "High Occupancy"
    elif bed_occupancy_rate >= 50:
        bed_status = "Moderate Occupancy"
    else:
        bed_status = "Low Occupancy"

    if total_doctors == 0:
        staffing_status = "No doctors configured"
    elif patients_per_doctor >= 50:
        staffing_status = "High Patient-to-Doctor Ratio"
    elif patients_per_doctor >= 25:
        staffing_status = "Moderate Patient-to-Doctor Ratio"
    else:
        staffing_status = "Lower Patient-to-Doctor Ratio"

    if emergency_case_rate >= 20:
        emergency_status = "High Emergency Case Rate"
    elif emergency_case_rate >= 10:
        emergency_status = "Moderate Emergency Case Rate"
    else:
        emergency_status = "Lower Emergency Case Rate"

    # ------------------------------------------------------------
    # KEY OBSERVATIONS
    # ------------------------------------------------------------

    observations = []

    observations.append(
        f"Bed occupancy is {bed_occupancy_rate}%."
    )

    observations.append(
        f"{available_beds} bed(s) are currently available."
    )

    observations.append(
        f"There are {patients_per_doctor} patients per doctor "
        "based on the supplied totals."
    )

    observations.append(
        f"Emergency cases represent {emergency_case_rate}% "
        "of the supplied patient count."
    )

    observations.append(
        f"Appointments per patient: "
        f"{appointments_per_patient}."
    )

    observations.append(discharge_note)

    # ------------------------------------------------------------
    # RECOMMENDATIONS
    # ------------------------------------------------------------

    recommendations = []

    if bed_occupancy_rate >= 90:
        recommendations.append(
            "Review bed capacity and patient flow because "
            "bed occupancy is very high."
        )
    elif bed_occupancy_rate >= 75:
        recommendations.append(
            "Monitor bed utilization closely and review "
            "upcoming admission demand."
        )
    else:
        recommendations.append(
            "Continue monitoring bed utilization and "
            "availability."
        )

    if total_doctors == 0:
        recommendations.append(
            "Review staffing data because no doctors were "
            "included in the supplied totals."
        )
    elif patients_per_doctor >= 50:
        recommendations.append(
            "Review staffing capacity because the supplied "
            "patient-to-doctor ratio is high."
        )

    if emergency_case_rate >= 20:
        recommendations.append(
            "Review emergency department capacity and "
            "emergency patient flow."
        )
    elif emergency_case_rate >= 10:
        recommendations.append(
            "Continue monitoring emergency case volume."
        )

    if total_beds == 0:
        recommendations.append(
            "Configure total hospital bed capacity before "
            "using bed utilization metrics."
        )

    # ------------------------------------------------------------
    # FINAL RESULT
    # ------------------------------------------------------------

    return {
        "success": True,

        "hospital_totals": {
            "total_patients": total_patients,
            "total_doctors": total_doctors,
            "total_appointments": total_appointments,
            "total_admissions": total_admissions,
            "total_discharges": total_discharges,
            "total_emergency_cases": total_emergency_cases,
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": available_beds,
        },

        "key_metrics": {
            "bed_occupancy_rate": bed_occupancy_rate,
            "bed_availability_rate": bed_availability_rate,
            "patients_per_doctor": patients_per_doctor,
            "appointments_per_patient": appointments_per_patient,
            "admissions_per_patient_percentage": admissions_per_patient,
            "discharges_per_admission_percentage": (
                discharges_per_admission
            ),
            "emergency_case_rate": emergency_case_rate,
        },

        "operational_status": {
            "bed_status": bed_status,
            "staffing_status": staffing_status,
            "emergency_status": emergency_status,
        },

        "observations": observations,

        "recommendations": recommendations,

        "disclaimer": (
            "This hospital analytics module is a rule-based "
            "operational analytics prototype. The results are "
            "informational and should not be treated as clinical "
            "diagnosis, treatment advice, or a substitute for "
            "professional healthcare judgment."
        ),
    }