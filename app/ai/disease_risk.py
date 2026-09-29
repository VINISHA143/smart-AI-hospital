from typing import List, Dict


RISK_RULES: Dict[str, Dict] = {
    "Diabetes": {
        "risk_factors": {
            "high blood sugar",
            "frequent urination",
            "excessive thirst",
            "family history of diabetes",
            "overweight",
            "obesity",
        },
        "weight": 15,
    },
    "Hypertension": {
        "risk_factors": {
            "high blood pressure",
            "family history of hypertension",
            "obesity",
            "smoking",
            "high salt intake",
            "stress",
        },
        "weight": 15,
    },
    "Heart Disease": {
        "risk_factors": {
            "chest pain",
            "shortness of breath",
            "high blood pressure",
            "diabetes",
            "smoking",
            "high cholesterol",
            "family history of heart disease",
            "obesity",
        },
        "weight": 12,
    },
    "Asthma": {
        "risk_factors": {
            "wheezing",
            "shortness of breath",
            "chronic cough",
            "chest tightness",
            "family history of asthma",
            "allergy",
        },
        "weight": 15,
    },
}


def normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def calculate_risk(
    age: int,
    symptoms: List[str],
    risk_factors: List[str],
) -> Dict:

    all_factors = {
        normalize(item)
        for item in symptoms + risk_factors
        if item and item.strip()
    }

    predictions = []

    for disease, rule in RISK_RULES.items():
        matched = all_factors.intersection(rule["risk_factors"])

        score = min(
            len(matched) * rule["weight"],
            100
        )

        if score >= 60:
            level = "High"
        elif score >= 30:
            level = "Moderate"
        elif score > 0:
            level = "Low"
        else:
            level = "Minimal"

        predictions.append({
            "disease": disease,
            "risk_percentage": score,
            "risk_level": level,
            "matched_factors": sorted(matched),
        })

    predictions.sort(
        key=lambda item: item["risk_percentage"],
        reverse=True,
    )

    return {
        "age": age,
        "predictions": predictions,
        "disclaimer": (
            "This risk estimate is for informational purposes only. "
            "It is not a diagnosis and should not replace evaluation "
            "by a qualified healthcare professional."
        ),
    }