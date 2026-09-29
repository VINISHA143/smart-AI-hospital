from typing import List, Dict


MEDICINE_RULES: Dict[str, Dict] = {
    "paracetamol": {
        "max_daily_dose_mg": 4000,
        "warnings": [
            "Avoid exceeding the recommended daily dose.",
            "Use caution in patients with significant liver disease.",
        ],
    },
    "ibuprofen": {
        "max_daily_dose_mg": 2400,
        "warnings": [
            "Use caution with kidney disease.",
            "Use caution with history of stomach ulcers or bleeding.",
        ],
    },
    "aspirin": {
        "max_daily_dose_mg": 4000,
        "warnings": [
            "May increase bleeding risk.",
            "Use caution in patients with bleeding disorders.",
        ],
    },
    "warfarin": {
        "max_daily_dose_mg": 20,
        "warnings": [
            "Requires careful clinical monitoring.",
            "May increase bleeding risk.",
        ],
    },
    "amoxicillin": {
        "max_daily_dose_mg": 6000,
        "warnings": [
            "Check for penicillin allergy before use.",
        ],
    },
}


DRUG_INTERACTIONS = {
    frozenset({"warfarin", "aspirin"}): (
        "Potentially increased bleeding risk when warfarin "
        "and aspirin are used together."
    ),
    frozenset({"warfarin", "ibuprofen"}): (
        "NSAIDs such as ibuprofen may increase bleeding risk "
        "when combined with warfarin."
    ),
    frozenset({"aspirin", "ibuprofen"}): (
        "Combined use may increase gastrointestinal bleeding "
        "and other adverse-effect risks."
    ),
}


def normalize(value: str) -> str:
    return " ".join(
        value.lower().strip().split()
    )


def check_prescription(
    medicines: List[Dict],
    allergies: List[str],
    conditions: List[str],
) -> Dict:

    normalized_allergies = {
        normalize(item)
        for item in allergies
        if item and item.strip()
    }

    normalized_conditions = {
        normalize(item)
        for item in conditions
        if item and item.strip()
    }

    normalized_medicines = []

    for medicine in medicines:
        name = normalize(medicine["name"])

        normalized_medicines.append({
            "name": name,
            "dose_mg": float(medicine["dose_mg"]),
            "frequency_per_day": int(
                medicine["frequency_per_day"]
            ),
        })

    warnings = []
    duplicate_medicines = []
    allergy_warnings = []
    dose_warnings = []
    interaction_warnings = []

    # --------------------------------------------------------
    # Duplicate medicine check
    # --------------------------------------------------------

    medicine_names = [
        medicine["name"]
        for medicine in normalized_medicines
    ]

    for name in set(medicine_names):
        if medicine_names.count(name) > 1:
            duplicate_medicines.append(name)

            warnings.append(
                f"Duplicate medicine detected: {name}."
            )

    # --------------------------------------------------------
    # Medicine checks
    # --------------------------------------------------------

    for medicine in normalized_medicines:

        name = medicine["name"]
        dose_mg = medicine["dose_mg"]
        frequency = medicine["frequency_per_day"]

        daily_dose = dose_mg * frequency

        # Allergy check
        if name in normalized_allergies:
            warning = (
                f"Allergy warning: patient reports an allergy "
                f"to {name}."
            )

            allergy_warnings.append(warning)
            warnings.append(warning)

        # Known medicine rules
        rule = MEDICINE_RULES.get(name)

        if rule:

            max_daily_dose = rule["max_daily_dose_mg"]

            if daily_dose > max_daily_dose:

                warning = (
                    f"Dose warning: {name} daily dose "
                    f"({daily_dose} mg) exceeds the configured "
                    f"prototype limit of {max_daily_dose} mg."
                )

                dose_warnings.append(warning)
                warnings.append(warning)

            for medicine_warning in rule["warnings"]:

                # Basic condition-based warnings
                if (
                    "liver" in medicine_warning.lower()
                    and (
                        "liver disease"
                        in normalized_conditions
                    )
                ):
                    warnings.append(
                        f"{name}: {medicine_warning}"
                    )

                elif (
                    "kidney" in medicine_warning.lower()
                    and (
                        "kidney disease"
                        in normalized_conditions
                    )
                ):
                    warnings.append(
                        f"{name}: {medicine_warning}"
                    )

                elif (
                    "ulcer" in medicine_warning.lower()
                    and (
                        "stomach ulcer"
                        in normalized_conditions
                    )
                ):
                    warnings.append(
                        f"{name}: {medicine_warning}"
                    )

    # --------------------------------------------------------
    # Drug interaction check
    # --------------------------------------------------------

    unique_medicines = set(medicine_names)

    for interaction_pair, message in DRUG_INTERACTIONS.items():

        if interaction_pair.issubset(
            unique_medicines
        ):
            interaction_warnings.append(message)
            warnings.append(message)

    # --------------------------------------------------------
    # Safety level
    # --------------------------------------------------------

    if allergy_warnings:
        safety_level = "High"

    elif interaction_warnings or dose_warnings:
        safety_level = "High"

    elif duplicate_medicines:
        safety_level = "Moderate"

    elif warnings:
        safety_level = "Moderate"

    else:
        safety_level = "Low"

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    if safety_level == "High":
        recommendation = (
            "Prescription requires clinical review before use. "
            "Do not rely on this automated checker for prescribing "
            "or medication decisions."
        )

    elif safety_level == "Moderate":
        recommendation = (
            "Potential safety concerns were detected. "
            "A qualified healthcare professional should review "
            "the prescription."
        )

    else:
        recommendation = (
            "No major issues were detected by the configured "
            "prototype rules. Clinical review is still required."
        )

    return {
        "success": True,
        "safety_level": safety_level,
        "medicines_checked": normalized_medicines,
        "duplicate_medicines": duplicate_medicines,
        "allergy_warnings": allergy_warnings,
        "dose_warnings": dose_warnings,
        "interaction_warnings": interaction_warnings,
        "warnings": warnings,
        "recommendation": recommendation,
        "disclaimer": (
            "This automated checker is a prototype for informational "
            "purposes only. It does not replace a pharmacist, doctor, "
            "clinical decision-support system, or official medication "
            "reference."
        ),
    }