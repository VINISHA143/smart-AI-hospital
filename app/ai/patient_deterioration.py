from typing import Dict


def calculate_deterioration_risk(
    heart_rate: float,
    systolic_bp: float,
    oxygen_saturation: float,
    respiratory_rate: float,
    temperature: float,
    consciousness: str,
) -> Dict:

    score = 0
    risk_factors = []

    consciousness_normalized = consciousness.strip().lower()

    # Heart rate
    if heart_rate < 50 or heart_rate > 120:
        score += 20
        risk_factors.append("Abnormal heart rate")
    elif heart_rate < 60 or heart_rate > 100:
        score += 10
        risk_factors.append("Heart rate outside normal range")

    # Systolic blood pressure
    if systolic_bp < 90 or systolic_bp > 180:
        score += 25
        risk_factors.append("Significantly abnormal systolic blood pressure")
    elif systolic_bp < 100 or systolic_bp > 140:
        score += 10
        risk_factors.append("Systolic blood pressure outside normal range")

    # Oxygen saturation
    if oxygen_saturation < 90:
        score += 30
        risk_factors.append("Critically low oxygen saturation")
    elif oxygen_saturation < 94:
        score += 20
        risk_factors.append("Low oxygen saturation")

    # Respiratory rate
    if respiratory_rate < 8 or respiratory_rate > 30:
        score += 25
        risk_factors.append("Significantly abnormal respiratory rate")
    elif respiratory_rate < 12 or respiratory_rate > 20:
        score += 10
        risk_factors.append("Respiratory rate outside normal range")

    # Temperature
    if temperature < 35 or temperature >= 40:
        score += 20
        risk_factors.append("Significantly abnormal temperature")
    elif temperature < 36 or temperature > 37.5:
        score += 10
        risk_factors.append("Temperature outside normal range")

    # Consciousness
    if consciousness_normalized in {
        "unconscious",
        "unresponsive",
        "confused",
        "altered",
        "drowsy",
    }:
        score += 30
        risk_factors.append("Altered level of consciousness")

    score = min(score, 100)

    if score >= 60:
        risk_level = "High"
        recommendation = (
            "Multiple deterioration risk factors detected. "
            "Prompt clinical assessment is recommended."
        )
    elif score >= 30:
        risk_level = "Moderate"
        recommendation = (
            "Potential deterioration risk detected. "
            "Continue close monitoring and consider clinical review."
        )
    elif score > 0:
        risk_level = "Low"
        recommendation = (
            "Some abnormal findings are present. "
            "Continue monitoring and reassess as clinically appropriate."
        )
    else:
        risk_level = "Minimal"
        recommendation = (
            "No significant deterioration risk factors were detected "
            "using the configured prototype rules."
        )

    return {
        "success": True,
        "deterioration_score": score,
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "vital_signs": {
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "oxygen_saturation": oxygen_saturation,
            "respiratory_rate": respiratory_rate,
            "temperature": temperature,
            "consciousness": consciousness,
        },
        "recommendation": recommendation,
        "disclaimer": (
            "This deterioration prediction is a rule-based prototype "
            "for informational purposes only. It is not a validated "
            "clinical prediction model and must not replace assessment "
            "or clinical judgment by a qualified healthcare professional."
        ),
    }