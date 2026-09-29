from typing import List, Dict


REFERENCE_RANGES: Dict[str, Dict] = {
    "hemoglobin": {
        "min": 12.0,
        "max": 17.5,
        "unit": "g/dL",
    },
    "glucose": {
        "min": 70.0,
        "max": 140.0,
        "unit": "mg/dL",
    },
    "cholesterol": {
        "min": 0.0,
        "max": 200.0,
        "unit": "mg/dL",
    },
    "systolic_bp": {
        "min": 90.0,
        "max": 120.0,
        "unit": "mmHg",
    },
    "diastolic_bp": {
        "min": 60.0,
        "max": 80.0,
        "unit": "mmHg",
    },
}


def normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def analyze_medical_report(
    parameters: List[Dict]
) -> Dict:

    abnormal_parameters = []
    normal_parameters = []

    for parameter in parameters:

        name = normalize(parameter["name"])
        value = float(parameter["value"])

        reference = REFERENCE_RANGES.get(name)

        if not reference:
            normal_parameters.append({
                "parameter": name,
                "value": value,
                "status": "Reference range unavailable",
            })
            continue

        minimum = reference["min"]
        maximum = reference["max"]

        if value < minimum:
            status = "Low"

            abnormal_parameters.append({
                "parameter": name,
                "value": value,
                "unit": reference["unit"],
                "status": status,
                "reference_range": f"{minimum} - {maximum}",
            })

        elif value > maximum:
            status = "High"

            abnormal_parameters.append({
                "parameter": name,
                "value": value,
                "unit": reference["unit"],
                "status": status,
                "reference_range": f"{minimum} - {maximum}",
            })

        else:
            normal_parameters.append({
                "parameter": name,
                "value": value,
                "unit": reference["unit"],
                "status": "Normal",
            })

    abnormal_count = len(abnormal_parameters)

    if abnormal_count >= 3:
        severity = "High"
    elif abnormal_count == 2:
        severity = "Moderate"
    elif abnormal_count == 1:
        severity = "Low"
    else:
        severity = "Normal"

    if severity == "High":
        recommendation = (
            "Multiple abnormal parameters detected. "
            "Medical evaluation is recommended."
        )
    elif severity == "Moderate":
        recommendation = (
            "Some abnormal parameters were detected. "
            "Consider discussing the results with a healthcare professional."
        )
    elif severity == "Low":
        recommendation = (
            "A minor abnormality was detected. "
            "Consider monitoring and discussing it with a healthcare professional."
        )
    else:
        recommendation = (
            "No abnormalities were detected within the configured "
            "reference ranges."
        )

    return {
        "success": True,
        "severity": severity,
        "total_parameters": len(parameters),
        "abnormal_count": abnormal_count,
        "abnormal_parameters": abnormal_parameters,
        "normal_parameters": normal_parameters,
        "recommendation": recommendation,
        "disclaimer": (
            "This automated analysis is informational only. "
            "Reference ranges can vary by laboratory, age, sex, "
            "and clinical context. It is not a medical diagnosis."
        ),
    }