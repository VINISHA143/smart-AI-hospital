from typing import List, Dict


CARE_PLAN_RULES: Dict[str, Dict] = {
    "diabetes": {
        "goals": [
            "Monitor blood glucose regularly.",
            "Follow the prescribed diabetes management plan.",
            "Maintain a healthy diet and appropriate physical activity."
        ],
        "monitoring": [
            "Blood glucose monitoring",
            "Weight monitoring",
            "Regular clinical follow-up"
        ],
        "education": [
            "Diabetes self-management education",
            "Medication adherence",
            "Recognition of symptoms of abnormal blood glucose"
        ]
    },

    "hypertension": {
        "goals": [
            "Monitor blood pressure regularly.",
            "Follow the prescribed treatment plan.",
            "Maintain a heart-healthy lifestyle."
        ],
        "monitoring": [
            "Blood pressure monitoring",
            "Weight monitoring",
            "Regular clinical follow-up"
        ],
        "education": [
            "Low-sodium lifestyle education",
            "Medication adherence",
            "Home blood pressure monitoring"
        ]
    },

    "asthma": {
        "goals": [
            "Maintain adequate respiratory control.",
            "Follow the prescribed asthma management plan.",
            "Identify and avoid known triggers."
        ],
        "monitoring": [
            "Breathing symptoms",
            "Frequency of respiratory symptoms",
            "Response to prescribed treatment"
        ],
        "education": [
            "Inhaler technique",
            "Trigger avoidance",
            "Recognition of worsening respiratory symptoms"
        ]
    },

    "heart disease": {
        "goals": [
            "Monitor cardiovascular symptoms.",
            "Follow the prescribed treatment plan.",
            "Maintain appropriate lifestyle measures."
        ],
        "monitoring": [
            "Blood pressure",
            "Heart rate",
            "Cardiovascular symptoms"
        ],
        "education": [
            "Medication adherence",
            "Heart-healthy lifestyle",
            "Recognition of concerning symptoms"
        ]
    }
}


def normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def generate_care_plan(
    diagnoses: List[str],
    symptoms: List[str],
    medications: List[str],
    chronic_conditions: List[str],
) -> Dict:

    normalized_diagnoses = [
        normalize(item)
        for item in diagnoses
        if item and item.strip()
    ]

    normalized_symptoms = [
        normalize(item)
        for item in symptoms
        if item and item.strip()
    ]

    normalized_medications = [
        normalize(item)
        for item in medications
        if item and item.strip()
    ]

    normalized_conditions = [
        normalize(item)
        for item in chronic_conditions
        if item and item.strip()
    ]

    all_conditions = list(
        dict.fromkeys(
            normalized_diagnoses + normalized_conditions
        )
    )

    goals = []
    monitoring = []
    education = []
    matched_conditions = []

    for condition in all_conditions:
        rule = CARE_PLAN_RULES.get(condition)

        if rule:
            matched_conditions.append(condition)

            goals.extend(rule["goals"])
            monitoring.extend(rule["monitoring"])
            education.extend(rule["education"])

    # General care-plan goals when no specific rule matches
    if not goals:
        goals.extend([
            "Monitor the patient's reported symptoms.",
            "Follow the treatment plan provided by the healthcare professional.",
            "Attend scheduled medical follow-up appointments."
        ])

    if not monitoring:
        monitoring.extend([
            "Monitor symptom progression.",
            "Monitor response to treatment.",
            "Routine clinical follow-up"
        ])

    if not education:
        education.extend([
            "Medication adherence",
            "Understanding warning symptoms",
            "Following healthcare professional instructions"
        ])

    # Medication-related plan
    medication_plan = []

    if normalized_medications:
        medication_plan.append(
            "Continue medications only as prescribed "
            "by the treating healthcare professional."
        )
        medication_plan.append(
            "Monitor for medication-related problems "
            "and report concerning symptoms to a healthcare professional."
        )
    else:
        medication_plan.append(
            "No medications were supplied for this care-plan assessment."
        )

    # Symptom-related recommendations
    symptom_recommendations = []

    if normalized_symptoms:
        symptom_recommendations.append(
            "Monitor the reported symptoms for persistence or worsening."
        )

        symptom_recommendations.append(
            "Seek professional medical evaluation if symptoms "
            "worsen or new concerning symptoms develop."
        )
    else:
        symptom_recommendations.append(
            "No symptoms were supplied for this care-plan assessment."
        )

    # Remove duplicates while preserving order
    goals = list(dict.fromkeys(goals))
    monitoring = list(dict.fromkeys(monitoring))
    education = list(dict.fromkeys(education))

    if matched_conditions:
        care_plan_status = "Condition-Specific Plan Generated"
    else:
        care_plan_status = "General Care Plan Generated"

    return {
        "success": True,
        "care_plan_status": care_plan_status,

        "patient_information": {
            "diagnoses": normalized_diagnoses,
            "symptoms": normalized_symptoms,
            "medications": normalized_medications,
            "chronic_conditions": normalized_conditions,
        },

        "matched_conditions": matched_conditions,

        "care_goals": goals,

        "monitoring_plan": monitoring,

        "medication_plan": medication_plan,

        "symptom_recommendations": symptom_recommendations,

        "patient_education": education,

        "follow_up_plan": (
            "Schedule follow-up according to the patient's "
            "clinical condition and treatment requirements."
        ),

        "care_plan_summary": (
            "A rule-based care plan has been generated from "
            "the supplied diagnoses, symptoms, medications, "
            "and chronic conditions."
        ),

        "disclaimer": (
            "This care plan is an informational rule-based prototype. "
            "It is not a personalized medical treatment plan and "
            "must not replace assessment, diagnosis, treatment, "
            "or clinical judgment by a qualified healthcare professional."
        ),
    }