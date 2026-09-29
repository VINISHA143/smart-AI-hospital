from typing import List, Dict


EMERGENCY_KEYWORDS = {
    "severe chest pain",
    "difficulty breathing",
    "severe shortness of breath",
    "loss of consciousness",
    "fainting",
    "seizure",
    "blue lips",
    "severe bleeding",
    "coughing blood",
    "vomiting blood",
    "sudden weakness",
    "sudden numbness",
    "difficulty speaking",
}


GENERAL_RESPONSES: Dict[str, str] = {
    "fever": (
        "Fever can occur with infections and other conditions. "
        "Monitor the temperature, maintain adequate hydration, "
        "and seek medical evaluation if it is persistent, severe, "
        "or associated with concerning symptoms."
    ),
    "cough": (
        "Cough can have many causes, including infections, allergies, "
        "asthma, or irritation. Monitor its duration and severity. "
        "Medical evaluation is recommended if it persists or worsens."
    ),
    "headache": (
        "Headaches can have many causes. Rest, hydration, and monitoring "
        "may be appropriate for mild symptoms, but severe, sudden, or "
        "unusual headaches require medical evaluation."
    ),
    "stomach pain": (
        "Stomach pain can have many possible causes. Monitor its severity "
        "and associated symptoms. Severe or persistent abdominal pain "
        "should be evaluated by a healthcare professional."
    ),
    "abdominal pain": (
        "Abdominal pain can have many possible causes. Severe, persistent, "
        "or worsening pain should be assessed by a healthcare professional."
    ),
    "dizziness": (
        "Dizziness can result from dehydration, low blood pressure, "
        "medications, or other conditions. If it is severe, recurrent, "
        "or associated with fainting or neurological symptoms, seek medical care."
    ),
    "vomiting": (
        "Vomiting can occur with infections, gastrointestinal conditions, "
        "medications, and other causes. Maintain hydration if possible. "
        "Persistent vomiting or signs of dehydration require medical evaluation."
    ),
}


def normalize(value: str) -> str:
    return " ".join(
        value.lower().strip().split()
    )


def detect_emergency(message: str) -> List[str]:
    normalized_message = normalize(message)

    matches = []

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in normalized_message:
            matches.append(keyword)

    return sorted(matches)


def generate_chat_response(
    message: str,
    symptoms: List[str],
    medical_context: Dict,
) -> Dict:

    normalized_message = normalize(message)

    emergency_matches = detect_emergency(
        normalized_message
    )

    # --------------------------------------------------------
    # Emergency detection
    # --------------------------------------------------------

    if emergency_matches:

        return {
            "success": True,
            "response_type": "Emergency",
            "message": (
                "The information provided includes potentially "
                "serious symptoms. Please seek emergency medical "
                "care immediately or contact your local emergency "
                "services."
            ),
            "detected_concerns": emergency_matches,
            "recommended_action": (
                "Immediate professional medical assessment is recommended."
            ),
            "disclaimer": (
                "This medical chat assistant is an informational "
                "prototype and does not replace emergency medical care."
            ),
        }

    # --------------------------------------------------------
    # Context-based response
    # --------------------------------------------------------

    detected_topics = []

    for keyword, response in GENERAL_RESPONSES.items():

        if keyword in normalized_message:

            detected_topics.append({
                "topic": keyword,
                "response": response,
            })

    # --------------------------------------------------------
    # Symptom context
    # --------------------------------------------------------

    normalized_symptoms = [
        normalize(symptom)
        for symptom in symptoms
        if symptom and symptom.strip()
    ]

    for symptom in normalized_symptoms:

        if symptom in GENERAL_RESPONSES:

            if not any(
                item["topic"] == symptom
                for item in detected_topics
            ):
                detected_topics.append({
                    "topic": symptom,
                    "response": GENERAL_RESPONSES[symptom],
                })

    # --------------------------------------------------------
    # Build response
    # --------------------------------------------------------

    if detected_topics:

        response_text = " ".join(
            item["response"]
            for item in detected_topics[:3]
        )

    else:

        response_text = (
            "I can provide general informational guidance about "
            "symptoms, medical reports, medications, appointments, "
            "and emergency warning signs. Please provide more "
            "specific information about your concern."
        )

    # --------------------------------------------------------
    # Medical context
    # --------------------------------------------------------

    context_notes = []

    if medical_context:

        risk_level = medical_context.get(
            "risk_level"
        )

        triage_level = medical_context.get(
            "triage_level"
        )

        report_severity = medical_context.get(
            "report_severity"
        )

        if risk_level:
            context_notes.append(
                f"Reported health risk level: {risk_level}."
            )

        if triage_level:
            context_notes.append(
                f"Reported triage level: {triage_level}."
            )

        if report_severity:
            context_notes.append(
                f"Medical report severity: {report_severity}."
            )

    if context_notes:

        response_text += (
            " Based on the supplied context, "
            + " ".join(context_notes)
            + " These values should be reviewed by a qualified "
              "healthcare professional."
        )

    return {
        "success": True,
        "response_type": "General Medical Information",
        "message": response_text,
        "detected_topics": [
            item["topic"]
            for item in detected_topics[:3]
        ],
        "recommended_action": (
            "Seek professional medical evaluation if symptoms "
            "persist, worsen, or cause concern."
        ),
        "disclaimer": (
            "This medical chat assistant provides general "
            "informational guidance only. It does not provide "
            "a diagnosis, prescribe treatment, or replace "
            "a qualified healthcare professional."
        ),
    }