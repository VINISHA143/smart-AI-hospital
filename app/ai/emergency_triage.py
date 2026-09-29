from typing import List, Dict


EMERGENCY_RULES: Dict[str, List[str]] = {
    "Critical Emergency": [
        "loss of consciousness",
        "fainting",
        "seizure",
        "severe bleeding",
        "coughing blood",
        "vomiting blood",
        "blue lips",
    ],

    "Breathing Emergency": [
        "severe shortness of breath",
        "difficulty breathing",
        "unable to breathe",
    ],

    "Cardiac Emergency": [
        "severe chest pain",
        "chest pain with sweating",
        "chest pain with shortness of breath",
    ],

    "Neurological Emergency": [
        "sudden weakness",
        "sudden numbness",
        "difficulty speaking",
        "facial drooping",
    ],
}


def normalize(value: str) -> str:
    return " ".join(
        value.lower().strip().split()
    )


def triage_emergency(
    symptoms: List[str],
) -> Dict:

    normalized_symptoms = [
        normalize(symptom)
        for symptom in symptoms
        if symptom and symptom.strip()
    ]

    emergency_matches = []
    emergency_categories = []

    for category, rules in EMERGENCY_RULES.items():

        matched = [
            symptom
            for symptom in normalized_symptoms
            if symptom in rules
        ]

        if matched:
            emergency_categories.append(category)

            emergency_matches.extend(
                matched
            )

    emergency_matches = list(
        dict.fromkeys(emergency_matches)
    )

    # --------------------------------------------------------
    # Determine triage level
    # --------------------------------------------------------

    if emergency_matches:
        triage_level = "Emergency"

    elif any(
        symptom in {
            "chest pain",
            "shortness of breath",
            "high fever",
            "persistent vomiting",
            "severe abdominal pain",
        }
        for symptom in normalized_symptoms
    ):
        triage_level = "Urgent"

    elif any(
        symptom in {
            "fever",
            "cough",
            "vomiting",
            "diarrhea",
            "moderate pain",
            "dizziness",
            "weakness",
        }
        for symptom in normalized_symptoms
    ):
        triage_level = "Moderate"

    else:
        triage_level = "Low"

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    if triage_level == "Emergency":

        recommendation = (
            "Seek emergency medical care immediately. "
            "Contact local emergency services or go to the "
            "nearest emergency department."
        )

    elif triage_level == "Urgent":

        recommendation = (
            "Prompt medical evaluation is recommended. "
            "Seek urgent medical care, especially if symptoms "
            "are worsening."
        )

    elif triage_level == "Moderate":

        recommendation = (
            "Consider medical evaluation if symptoms persist, "
            "worsen, or new symptoms develop."
        )

    else:

        recommendation = (
            "Monitor symptoms and consider routine medical "
            "evaluation if symptoms persist."
        )

    return {
        "success": True,
        "symptoms": normalized_symptoms,
        "triage_level": triage_level,
        "emergency_categories": emergency_categories,
        "emergency_symptoms": emergency_matches,
        "recommendation": recommendation,
        "disclaimer": (
            "This automated triage tool is an informational "
            "prototype only. It is not a medical diagnosis "
            "and must not replace professional emergency "
            "assessment or clinical judgment."
        ),
    }