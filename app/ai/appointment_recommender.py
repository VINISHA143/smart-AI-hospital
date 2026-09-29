from typing import List, Dict


SPECIALTY_RULES: Dict[str, Dict] = {
    "Cardiology": {
        "symptoms": {
            "chest pain",
            "severe chest pain",
            "palpitations",
            "shortness of breath",
            "high blood pressure",
        },
        "reason": "Symptoms may require cardiovascular evaluation.",
    },

    "Pulmonology": {
        "symptoms": {
            "wheezing",
            "difficulty breathing",
            "shortness of breath",
            "chronic cough",
            "persistent cough",
        },
        "reason": "Symptoms may require respiratory evaluation.",
    },

    "General Medicine": {
        "symptoms": {
            "fever",
            "cough",
            "body ache",
            "fatigue",
            "headache",
            "sore throat",
            "weakness",
        },
        "reason": "Symptoms are commonly evaluated by General Medicine.",
    },

    "Gastroenterology": {
        "symptoms": {
            "stomach pain",
            "abdominal pain",
            "diarrhea",
            "persistent vomiting",
            "nausea",
        },
        "reason": "Symptoms may require gastrointestinal evaluation.",
    },

    "Neurology": {
        "symptoms": {
            "severe headache",
            "migraine",
            "seizure",
            "sudden weakness",
            "sudden numbness",
            "difficulty speaking",
            "dizziness",
        },
        "reason": "Symptoms may require neurological evaluation.",
    },

    "Dermatology": {
        "symptoms": {
            "skin rash",
            "itching",
            "itchy skin",
            "skin irritation",
        },
        "reason": "Symptoms may require dermatological evaluation.",
    },

    "ENT": {
        "symptoms": {
            "ear pain",
            "hearing loss",
            "sinus pain",
            "blocked nose",
            "sore throat",
        },
        "reason": "Symptoms may require ear, nose, and throat evaluation.",
    },
}


EMERGENCY_SYMPTOMS = {
    "severe chest pain",
    "chest pain with sweating",
    "severe shortness of breath",
    "difficulty breathing",
    "loss of consciousness",
    "fainting",
    "seizure",
    "sudden weakness",
    "sudden numbness",
    "difficulty speaking",
    "blue lips",
    "severe bleeding",
    "coughing blood",
    "vomiting blood",
}


def normalize(value: str) -> str:
    return " ".join(
        value.lower().strip().split()
    )


def recommend_appointment(
    symptoms: List[str],
    urgency: str = "Auto",
    preferred_department: str | None = None,
) -> Dict:

    normalized_symptoms = [
        normalize(symptom)
        for symptom in symptoms
        if symptom and symptom.strip()
    ]

    normalized_urgency = normalize(urgency)

    emergency_matches = [
        symptom
        for symptom in normalized_symptoms
        if symptom in EMERGENCY_SYMPTOMS
    ]

    # --------------------------------------------------------
    # Emergency override
    # --------------------------------------------------------

    if emergency_matches or normalized_urgency == "emergency":

        return {
            "success": True,
            "recommended_department": "Emergency Department",
            "recommended_specialty": "Emergency Medicine",
            "priority": "Emergency",
            "matched_symptoms": emergency_matches,
            "reason": (
                "Emergency indicators were detected. "
                "Immediate emergency medical assessment is recommended."
            ),
            "next_step": (
                "Proceed to the nearest emergency department "
                "or contact local emergency services."
            ),
            "disclaimer": (
                "This recommendation is informational only and "
                "does not replace professional medical triage."
            ),
        }

    # --------------------------------------------------------
    # Preferred department
    # --------------------------------------------------------

    if preferred_department:

        department = preferred_department.strip()

        return {
            "success": True,
            "recommended_department": department,
            "recommended_specialty": department,
            "priority": (
                "Urgent"
                if normalized_urgency == "urgent"
                else "Routine"
            ),
            "matched_symptoms": [],
            "reason": (
                "The requested department was retained as the "
                "preferred department."
            ),
            "next_step": (
                f"Schedule an appointment with {department}."
            ),
            "disclaimer": (
                "This recommendation is informational only and "
                "does not replace professional medical advice."
            ),
        }

    # --------------------------------------------------------
    # Specialty matching
    # --------------------------------------------------------

    symptom_set = set(normalized_symptoms)

    recommendations = []

    for specialty, rule in SPECIALTY_RULES.items():

        matched = symptom_set.intersection(
            rule["symptoms"]
        )

        if matched:

            recommendations.append({
                "specialty": specialty,
                "matched_symptoms": sorted(matched),
                "score": len(matched),
                "reason": rule["reason"],
            })

    recommendations.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # --------------------------------------------------------
    # No specialty match
    # --------------------------------------------------------

    if not recommendations:

        return {
            "success": True,
            "recommended_department": "General Medicine",
            "recommended_specialty": "General Physician",
            "priority": (
                "Urgent"
                if normalized_urgency == "urgent"
                else "Routine"
            ),
            "matched_symptoms": [],
            "reason": (
                "No specific specialty matched the supplied "
                "symptoms. General Medicine is recommended "
                "as the initial point of evaluation."
            ),
            "next_step": (
                "Schedule an appointment with General Medicine."
            ),
            "disclaimer": (
                "This recommendation is informational only and "
                "does not replace professional medical advice."
            ),
        }

    best = recommendations[0]

    priority = "Routine"

    if normalized_urgency == "urgent":
        priority = "Urgent"

    elif normalized_urgency == "moderate":
        priority = "Moderate"

    return {
        "success": True,
        "recommended_department": best["specialty"],
        "recommended_specialty": best["specialty"],
        "priority": priority,
        "matched_symptoms": best["matched_symptoms"],
        "reason": best["reason"],
        "next_step": (
            f"Schedule an appointment with "
            f"{best['specialty']}."
        ),
        "alternative_specialties": [
            item["specialty"]
            for item in recommendations[1:4]
        ],
        "disclaimer": (
            "This recommendation is informational only and "
            "does not replace professional medical advice."
        ),
    }