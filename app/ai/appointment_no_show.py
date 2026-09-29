from typing import Dict, List


NO_SHOW_RISK_WEIGHTS: Dict[str, int] = {
    "previous no show": 25,
    "multiple no shows": 35,
    "appointment rescheduled": 15,
    "long waiting time": 10,
    "transportation problem": 15,
    "cost concern": 15,
    "forgetfulness": 20,
    "distance concern": 10,
    "multiple appointments": 10,
    "weekend appointment": 5,
}


def normalize(value: str) -> str:
    return " ".join(
        value.lower().strip().split()
    )


def calculate_appointment_no_show_risk(
    previous_no_shows: int,
    previous_appointments: int,
    rescheduled_appointments: int,
    waiting_time_minutes: int,
    barriers: List[str],
    appointments_same_day: int,
    weekend_appointment: bool,
) -> Dict:

    normalized_barriers = {
        normalize(item)
        for item in barriers
        if item and item.strip()
    }

    score = 0
    matched_factors = []
    recommendations = []

    if previous_no_shows >= 3:
        score += NO_SHOW_RISK_WEIGHTS["multiple no shows"]
        matched_factors.append({
            "factor": "multiple previous no shows",
            "value": previous_no_shows,
            "weight": NO_SHOW_RISK_WEIGHTS["multiple no shows"],
        })
    elif previous_no_shows >= 1:
        score += NO_SHOW_RISK_WEIGHTS["previous no show"]
        matched_factors.append({
            "factor": "previous no show",
            "value": previous_no_shows,
            "weight": NO_SHOW_RISK_WEIGHTS["previous no show"],
        })

    if previous_appointments >= 10:
        score += 10
        matched_factors.append({
            "factor": "high appointment history",
            "value": previous_appointments,
            "weight": 10,
        })

    if rescheduled_appointments >= 3:
        score += NO_SHOW_RISK_WEIGHTS["appointment rescheduled"]
        matched_factors.append({
            "factor": "multiple rescheduled appointments",
            "value": rescheduled_appointments,
            "weight": NO_SHOW_RISK_WEIGHTS[
                "appointment rescheduled"
            ],
        })
    elif rescheduled_appointments >= 1:
        score += 10
        matched_factors.append({
            "factor": "rescheduled appointment",
            "value": rescheduled_appointments,
            "weight": 10,
        })

    if waiting_time_minutes >= 120:
        score += NO_SHOW_RISK_WEIGHTS["long waiting time"]
        matched_factors.append({
            "factor": "long waiting time",
            "value": waiting_time_minutes,
            "weight": NO_SHOW_RISK_WEIGHTS["long waiting time"],
        })
    elif waiting_time_minutes >= 60:
        score += 5
        matched_factors.append({
            "factor": "moderate waiting time",
            "value": waiting_time_minutes,
            "weight": 5,
        })

    barrier_weights = {
        "transportation problem": NO_SHOW_RISK_WEIGHTS[
            "transportation problem"
        ],
        "cost concern": NO_SHOW_RISK_WEIGHTS[
            "cost concern"
        ],
        "forgetfulness": NO_SHOW_RISK_WEIGHTS[
            "forgetfulness"
        ],
        "distance concern": NO_SHOW_RISK_WEIGHTS[
            "distance concern"
        ],
    }

    for barrier, weight in barrier_weights.items():
        if barrier in normalized_barriers:
            score += weight

            matched_factors.append({
                "factor": barrier,
                "weight": weight,
            })

    if appointments_same_day >= 3:
        score += NO_SHOW_RISK_WEIGHTS[
            "multiple appointments"
        ]

        matched_factors.append({
            "factor": "multiple appointments same day",
            "value": appointments_same_day,
            "weight": NO_SHOW_RISK_WEIGHTS[
                "multiple appointments"
            ],
        })
    elif appointments_same_day == 2:
        score += 5

        matched_factors.append({
            "factor": "two appointments same day",
            "value": appointments_same_day,
            "weight": 5,
        })

    if weekend_appointment:
        score += NO_SHOW_RISK_WEIGHTS[
            "weekend appointment"
        ]

        matched_factors.append({
            "factor": "weekend appointment",
            "value": True,
            "weight": NO_SHOW_RISK_WEIGHTS[
                "weekend appointment"
            ],
        })

    score = min(score, 100)

    if score >= 60:
        risk_level = "High"
    elif score >= 30:
        risk_level = "Moderate"
    elif score > 0:
        risk_level = "Low"
    else:
        risk_level = "Minimal"

    if previous_no_shows > 0:
        recommendations.append(
            "Consider appointment reminders and "
            "confirmation before the scheduled visit."
        )

    if "forgetfulness" in normalized_barriers:
        recommendations.append(
            "Consider SMS, phone, or app-based appointment "
            "reminders."
        )

    if "transportation problem" in normalized_barriers:
        recommendations.append(
            "Consider transportation assistance or "
            "alternative appointment arrangements."
        )

    if "cost concern" in normalized_barriers:
        recommendations.append(
            "Consider discussing available financial "
            "assistance or payment options."
        )

    if "distance concern" in normalized_barriers:
        recommendations.append(
            "Consider a closer facility or telehealth "
            "option where clinically appropriate."
        )

    if rescheduled_appointments > 0:
        recommendations.append(
            "Confirm the patient's preferred appointment "
            "time before scheduling."
        )

    if waiting_time_minutes >= 60:
        recommendations.append(
            "Review appointment scheduling and waiting-time "
            "management."
        )

    if appointments_same_day >= 2:
        recommendations.append(
            "Review same-day appointment scheduling to "
            "reduce scheduling conflicts."
        )

    if risk_level == "High":
        overall_recommendation = (
            "High appointment no-show risk indicators were "
            "detected. Consider proactive appointment "
            "confirmation and patient support."
        )
    elif risk_level == "Moderate":
        overall_recommendation = (
            "Moderate appointment no-show risk indicators "
            "were detected. Reminder and follow-up "
            "strategies are recommended."
        )
    elif risk_level == "Low":
        overall_recommendation = (
            "Some appointment no-show risk factors were "
            "detected. Routine reminders may be helpful."
        )
    else:
        overall_recommendation = (
            "No significant appointment no-show risk "
            "indicators were detected by the configured "
            "prototype rules."
        )

    recommendations = list(
        dict.fromkeys(recommendations)
    )

    return {
        "success": True,
        "no_show_risk_score": score,
        "no_show_risk_level": risk_level,
        "appointment_information": {
            "previous_no_shows": previous_no_shows,
            "previous_appointments": previous_appointments,
            "rescheduled_appointments": rescheduled_appointments,
            "waiting_time_minutes": waiting_time_minutes,
            "appointments_same_day": appointments_same_day,
            "weekend_appointment": weekend_appointment,
        },
        "barriers": sorted(normalized_barriers),
        "matched_risk_factors": matched_factors,
        "recommendation": overall_recommendation,
        "support_recommendations": recommendations,
        "disclaimer": (
            "This appointment no-show risk assessment is "
            "an informational prototype based on supplied "
            "information. It is not a validated prediction "
            "model and must not be used as the sole basis "
            "for patient management or scheduling decisions."
        ),
    }