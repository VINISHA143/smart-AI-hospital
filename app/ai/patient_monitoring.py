from typing import Dict


def monitor_patient(
    heart_rate: float,
    systolic_bp: float,
    diastolic_bp: float,
    temperature: float,
    oxygen_saturation: float,
    respiratory_rate: float,
) -> Dict:

    observations = []
    abnormal_parameters = []
    warnings = []

    # Heart rate
    if heart_rate < 60:
        status = "Low"
        abnormal_parameters.append("heart_rate")
        warnings.append("Heart rate is below the configured normal range.")
    elif heart_rate > 100:
        status = "High"
        abnormal_parameters.append("heart_rate")
        warnings.append("Heart rate is above the configured normal range.")
    else:
        status = "Normal"

    observations.append({
        "parameter": "heart_rate",
        "value": heart_rate,
        "unit": "bpm",
        "status": status,
    })

    # Systolic blood pressure
    if systolic_bp < 90:
        status = "Low"
        abnormal_parameters.append("systolic_bp")
        warnings.append(
            "Systolic blood pressure is below the configured normal range."
        )
    elif systolic_bp > 140:
        status = "High"
        abnormal_parameters.append("systolic_bp")
        warnings.append(
            "Systolic blood pressure is above the configured normal range."
        )
    else:
        status = "Normal"

    observations.append({
        "parameter": "systolic_bp",
        "value": systolic_bp,
        "unit": "mmHg",
        "status": status,
    })

    # Diastolic blood pressure
    if diastolic_bp < 60:
        status = "Low"
        abnormal_parameters.append("diastolic_bp")
        warnings.append(
            "Diastolic blood pressure is below the configured normal range."
        )
    elif diastolic_bp > 90:
        status = "High"
        abnormal_parameters.append("diastolic_bp")
        warnings.append(
            "Diastolic blood pressure is above the configured normal range."
        )
    else:
        status = "Normal"

    observations.append({
        "parameter": "diastolic_bp",
        "value": diastolic_bp,
        "unit": "mmHg",
        "status": status,
    })

    # Temperature
    if temperature < 36.0:
        status = "Low"
        abnormal_parameters.append("temperature")
        warnings.append(
            "Temperature is below the configured normal range."
        )
    elif temperature > 37.5:
        status = "High"
        abnormal_parameters.append("temperature")
        warnings.append(
            "Temperature is above the configured normal range."
        )
    else:
        status = "Normal"

    observations.append({
        "parameter": "temperature",
        "value": temperature,
        "unit": "°C",
        "status": status,
    })

    # Oxygen saturation
    if oxygen_saturation < 90:
        status = "Critical Low"
        abnormal_parameters.append("oxygen_saturation")
        warnings.append(
            "Oxygen saturation is critically low according to "
            "the configured prototype threshold."
        )
    elif oxygen_saturation < 94:
        status = "Low"
        abnormal_parameters.append("oxygen_saturation")
        warnings.append(
            "Oxygen saturation is below the configured normal range."
        )
    else:
        status = "Normal"

    observations.append({
        "parameter": "oxygen_saturation",
        "value": oxygen_saturation,
        "unit": "%",
        "status": status,
    })

    # Respiratory rate
    if respiratory_rate < 12:
        status = "Low"
        abnormal_parameters.append("respiratory_rate")
        warnings.append(
            "Respiratory rate is below the configured normal range."
        )
    elif respiratory_rate > 20:
        status = "High"
        abnormal_parameters.append("respiratory_rate")
        warnings.append(
            "Respiratory rate is above the configured normal range."
        )
    else:
        status = "Normal"

    observations.append({
        "parameter": "respiratory_rate",
        "value": respiratory_rate,
        "unit": "breaths/min",
        "status": status,
    })

    # Overall monitoring level
    if any(
        observation["status"] == "Critical Low"
        for observation in observations
    ):
        monitoring_level = "Critical"
    elif len(abnormal_parameters) >= 3:
        monitoring_level = "High"
    elif len(abnormal_parameters) >= 1:
        monitoring_level = "Moderate"
    else:
        monitoring_level = "Normal"

    # Recommendation
    if monitoring_level == "Critical":
        recommendation = (
            "Critical vital-sign abnormality detected. "
            "Immediate professional medical assessment is recommended."
        )
    elif monitoring_level == "High":
        recommendation = (
            "Multiple vital-sign abnormalities detected. "
            "Prompt clinical review is recommended."
        )
    elif monitoring_level == "Moderate":
        recommendation = (
            "One or more vital-sign abnormalities detected. "
            "Continue monitoring and consider clinical evaluation."
        )
    else:
        recommendation = (
            "All supplied vital signs are within the configured "
            "prototype monitoring ranges."
        )

    return {
        "success": True,
        "monitoring_level": monitoring_level,
        "vital_signs": observations,
        "abnormal_parameters": abnormal_parameters,
        "warnings": warnings,
        "recommendation": recommendation,
        "disclaimer": (
            "This automated patient monitoring tool is a rule-based "
            "prototype for informational purposes only. Vital-sign "
            "interpretation depends on the patient's clinical context "
            "and must be reviewed by a qualified healthcare professional."
        ),
    }