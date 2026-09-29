from typing import List, Dict


# ============================================================
# SYMPTOM DATABASE
# ============================================================

SYMPTOM_DATABASE: Dict[str, Dict] = {
    "common_cold": {
        "name": "Common Cold",
        "symptoms": {
            "runny nose",
            "blocked nose",
            "sneezing",
            "sore throat",
            "cough",
            "mild fever",
        },
        "severity": "low",
    },

    "flu": {
        "name": "Influenza (Flu)",
        "symptoms": {
            "fever",
            "cough",
            "sore throat",
            "body ache",
            "fatigue",
            "headache",
            "chills",
        },
        "severity": "moderate",
    },

    "viral_fever": {
        "name": "Viral Fever",
        "symptoms": {
            "fever",
            "fatigue",
            "headache",
            "body ache",
            "chills",
            "loss of appetite",
        },
        "severity": "moderate",
    },

    "migraine": {
        "name": "Migraine",
        "symptoms": {
            "headache",
            "severe headache",
            "nausea",
            "vomiting",
            "sensitivity to light",
            "sensitivity to sound",
        },
        "severity": "moderate",
    },

    "gastroenteritis": {
        "name": "Gastroenteritis",
        "symptoms": {
            "nausea",
            "vomiting",
            "diarrhea",
            "stomach pain",
            "abdominal pain",
            "fever",
        },
        "severity": "moderate",
    },

    "allergy": {
        "name": "Allergic Reaction / Allergy",
        "symptoms": {
            "sneezing",
            "runny nose",
            "itchy eyes",
            "watery eyes",
            "skin rash",
            "itching",
        },
        "severity": "low",
    },

    "dehydration": {
        "name": "Dehydration",
        "symptoms": {
            "thirst",
            "dry mouth",
            "dizziness",
            "fatigue",
            "weakness",
            "reduced urination",
        },
        "severity": "moderate",
    },

    "pneumonia": {
        "name": "Pneumonia",
        "symptoms": {
            "fever",
            "cough",
            "shortness of breath",
            "chest pain",
            "chills",
            "fatigue",
        },
        "severity": "high",
    },

    "asthma": {
        "name": "Asthma Exacerbation",
        "symptoms": {
            "shortness of breath",
            "wheezing",
            "chest tightness",
            "cough",
        },
        "severity": "high",
    },
}


# ============================================================
# EMERGENCY SYMPTOMS
# ============================================================

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


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_symptom(symptom: str) -> str:
    return " ".join(
        symptom.lower().strip().split()
    )


def normalize_symptoms(symptoms: List[str]) -> List[str]:
    return list(
        dict.fromkeys(
            normalize_symptom(symptom)
            for symptom in symptoms
            if symptom and symptom.strip()
        )
    )


# ============================================================
# EMERGENCY DETECTION
# ============================================================

def detect_emergency(symptoms: List[str]) -> List[str]:
    matches = []

    for symptom in symptoms:
        if symptom in EMERGENCY_SYMPTOMS:
            matches.append(symptom)

    return matches


# ============================================================
# CONDITION ANALYSIS
# ============================================================

def analyze_conditions(symptoms: List[str]) -> List[Dict]:
    results = []

    symptom_set = set(symptoms)

    for condition in SYMPTOM_DATABASE.values():

        condition_symptoms = condition["symptoms"]

        matched = symptom_set.intersection(
            condition_symptoms
        )

        if not matched:
            continue

        score = (
            len(matched)
            / len(condition_symptoms)
        )

        results.append({
            "condition": condition["name"],
            "matched_symptoms": sorted(
                list(matched)
            ),
            "match_score": round(
                score * 100,
                2
            ),
            "severity": condition["severity"],
        })

    results.sort(
        key=lambda item: item["match_score"],
        reverse=True,
    )

    return results[:5]


# ============================================================
# URGENCY
# ============================================================

def determine_urgency(
    symptoms: List[str],
    possible_conditions: List[Dict],
) -> str:

    emergency_matches = detect_emergency(
        symptoms
    )

    if emergency_matches:
        return "Emergency"

    if any(
        condition["severity"] == "high"
        for condition in possible_conditions[:3]
    ):
        return "Urgent"

    if any(
        condition["severity"] == "moderate"
        for condition in possible_conditions[:3]
    ):
        return "Moderate"

    return "Low"


# ============================================================
# MAIN ANALYZER
#
# IMPORTANT:
# This accepts all arguments from app/api/ai.py.
# Extra arguments are safely supported.
# ============================================================

def analyze_symptoms(
    symptoms: List[str],
    age: int = 0,
    gender: str = "",
    duration_days: int = 1,
) -> Dict:

    normalized_symptoms = normalize_symptoms(
        symptoms
    )

    if not normalized_symptoms:
        return {
            "success": False,
            "message": "At least one symptom is required.",
        }

    emergency_matches = detect_emergency(
        normalized_symptoms
    )

    possible_conditions = analyze_conditions(
        normalized_symptoms
    )

    urgency = determine_urgency(
        normalized_symptoms,
        possible_conditions,
    )

    if urgency == "Emergency":

        recommendation = (
            "Seek emergency medical care immediately. "
            "Do not rely on this automated analysis."
        )

    elif urgency == "Urgent":

        recommendation = (
            "Arrange medical evaluation as soon as possible."
        )

    elif urgency == "Moderate":

        recommendation = (
            "Consider evaluation by a qualified healthcare "
            "professional, especially if symptoms persist "
            "or worsen."
        )

    else:

        recommendation = (
            "Monitor symptoms and consider routine medical "
            "evaluation if symptoms persist, worsen, or "
            "new symptoms develop."
        )

    return {
        "success": True,
        "symptoms": normalized_symptoms,
        "age": age,
        "gender": gender,
        "duration_days": duration_days,
        "emergency_symptoms": emergency_matches,
        "urgency": urgency,
        "possible_conditions": possible_conditions,
        "recommendation": recommendation,
        "disclaimer": (
            "This tool provides informational symptom "
            "analysis only. It is not a medical diagnosis "
            "and must not replace evaluation by a qualified "
            "healthcare professional."
        ),
    }