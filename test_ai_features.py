import os
import json
import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://127.0.0.1:8000"

# You can change these two values if your test admin account
# uses a different username/password.
USERNAME = os.getenv("TEST_USERNAME", "admin")
PASSWORD = os.getenv("TEST_PASSWORD", "admin")

TIMEOUT = 30


# ============================================================
# TERMINAL HELPERS
# ============================================================

def print_separator():
    print("=" * 70)


def print_section(number, title):
    print()
    print_separator()
    print(f"{number}. {title}")
    print_separator()


def print_json(data):
    try:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except Exception:
        print(data)


def result_status(response):
    return response.status_code == 200


# ============================================================
# HTTP HELPERS
# ============================================================

def post_json(session, endpoint, payload, token):
    url = f"{BASE_URL}{endpoint}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    print(f"POST {url}")
    print()
    print("REQUEST:")
    print_json(payload)
    print()

    try:
        response = session.post(
            url,
            json=payload,
            headers=headers,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        print("REQUEST ERROR:")
        print(str(exc))
        return None

    print(f"Status: {response.status_code}")

    try:
        data = response.json()
    except ValueError:
        data = response.text

    print_json(data)

    return response


def print_result(endpoint, response):
    if response is None:
        print()
        print("RESULT: FAIL")
        print(f"Endpoint: {endpoint}")
        print("Reason: Request could not be completed.")
        return False

    if response.status_code == 200:
        print()
        print("RESULT: PASS")
        print(f"Endpoint: {endpoint}")
        print("HTTP Status: 200")
        return True

    print()
    print("RESULT: FAIL")
    print(f"Endpoint: {endpoint}")
    print(f"HTTP Status: {response.status_code}")

    if response.status_code == 422:
        print()
        print("This is a FastAPI validation error.")
        print("Check the JSON field names against the Pydantic request model.")

    return False


# ============================================================
# LOGIN
# ============================================================

def login(session):
    print_section(0, "Admin Login")

    url = f"{BASE_URL}/auth/login"

    payload = {
        "username": USERNAME,
        "password": PASSWORD,
    }

    print(f"POST {url}")
    print()
    print("REQUEST:")
    print_json(payload)
    print()

    try:
        response = session.post(
            url,
            json=payload,
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        print("LOGIN REQUEST ERROR:")
        print(str(exc))
        return None

    print(f"Status: {response.status_code}")

    try:
        data = response.json()
    except ValueError:
        print(response.text)
        return None

    print_json(data)

    if response.status_code != 200:
        print()
        print("LOGIN FAILED")
        return None

    token = (
        data.get("access_token")
        or data.get("token")
        or data.get("accessToken")
    )

    if not token:
        print()
        print("LOGIN SUCCEEDED BUT NO TOKEN WAS FOUND.")
        print("Check your /auth/login response field name.")
        return None

    print()
    print("LOGIN: PASS")

    return token


# ============================================================
# MAIN TEST FUNCTION
# ============================================================

def main():

    session = requests.Session()

    token = login(session)

    if not token:
        print()
        print_separator()
        print("TESTING STOPPED")
        print_separator()
        print("Could not obtain authentication token.")
        print()
        print("If your admin password is different, run:")
        print()
        print('$env:TEST_PASSWORD="YOUR_PASSWORD"')
        print("python test_ai_features.py")
        print()
        return

    results = []

    # ========================================================
    # 1. SYMPTOM ANALYZER
    # ========================================================

    print_section(1, "Symptom Analyzer")

    payload = {
        "symptoms": [
            "fatigue",
            "frequent urination",
        ],
        "age": 45,
        "gender": "male",
        "duration_days": 7,
    }

    response = post_json(
        session,
        "/ai/symptom-analyzer",
        payload,
        token,
    )

    passed = print_result(
        "/ai/symptom-analyzer",
        response,
    )

    results.append(
        ("Symptom Analyzer", "/ai/symptom-analyzer", passed)
    )

    # ========================================================
    # 2. DISEASE RISK
    # ========================================================

    print_section(2, "Disease Risk")

    payload = {
        "symptoms": [
            "fatigue",
            "frequent urination",
        ],
        "age": 45,
        "gender": "male",
        "medical_history": [
            "diabetes",
            "hypertension",
        ],
    }

    response = post_json(
        session,
        "/ai/disease-risk",
        payload,
        token,
    )

    passed = print_result(
        "/ai/disease-risk",
        response,
    )

    results.append(
        ("Disease Risk", "/ai/disease-risk", passed)
    )

    # ========================================================
    # 3. MEDICAL REPORT ANALYZER
    # ========================================================

    print_section(3, "Medical Report Analyzer")

    payload = {
        "parameters": [
            {
                "name": "glucose",
                "value": 180,
            },
            {
                "name": "cholesterol",
                "value": 240,
            },
            {
                "name": "hemoglobin",
                "value": 13.5,
            },
        ]
    }

    response = post_json(
        session,
        "/ai/medical-report-analyzer",
        payload,
        token,
    )

    passed = print_result(
        "/ai/medical-report-analyzer",
        response,
    )

    results.append(
        (
            "Medical Report Analyzer",
            "/ai/medical-report-analyzer",
            passed,
        )
    )

    # ========================================================
    # 4. PRESCRIPTION SAFETY
    # ========================================================

    print_section(4, "Prescription Safety")

    payload = {
        "medicines": [
            {
                "name": "metformin",
                "dose_mg": 500,
                "frequency_per_day": 2,
            },
            {
                "name": "lisinopril",
                "dose_mg": 10,
                "frequency_per_day": 1,
            },
        ],
        "allergies": [],
        "medical_conditions": [
            "diabetes",
            "hypertension",
        ],
    }

    response = post_json(
        session,
        "/ai/prescription-safety",
        payload,
        token,
    )

    passed = print_result(
        "/ai/prescription-safety",
        response,
    )

    results.append(
        (
            "Prescription Safety",
            "/ai/prescription-safety",
            passed,
        )
    )

    # ========================================================
    # 5. EMERGENCY TRIAGE
    # ========================================================

    print_section(5, "Emergency Triage")

    # IMPORTANT:
    # The backend requires:
    # symptoms
    # severity
    # age
    # consciousness
    #
    # severity must be between 1 and 10.

    payload = {
        "symptoms": [
            "chest pain",
            "shortness of breath",
        ],
        "severity": 8,
        "age": 45,
        "consciousness": "normal",
    }

    response = post_json(
        session,
        "/ai/emergency-triage",
        payload,
        token,
    )

    passed = print_result(
        "/ai/emergency-triage",
        response,
    )

    results.append(
        (
            "Emergency Triage",
            "/ai/emergency-triage",
            passed,
        )
    )

    # ========================================================
    # 6. APPOINTMENT RECOMMENDATION
    # ========================================================

    print_section(6, "Appointment Recommendation")

    payload = {
        "symptoms": [
            "fatigue",
        ],
        "department": "General Medicine",
        "urgency": "Routine",
    }

    response = post_json(
        session,
        "/ai/appointment-recommendation",
        payload,
        token,
    )

    passed = print_result(
        "/ai/appointment-recommendation",
        response,
    )

    results.append(
        (
            "Appointment Recommendation",
            "/ai/appointment-recommendation",
            passed,
        )
    )

    # ========================================================
    # 7. HEALTH RISK SCORE
    # ========================================================

    print_section(7, "Health Risk Score")

    payload = {
        "age": 45,
        "bmi": 27.5,
        "blood_pressure": "140/90",
        "glucose": 180,
        "cholesterol": 240,
        "smoking": False,
        "diabetes": True,
        "hypertension": True,
        "heart_disease": False,
    }

    response = post_json(
        session,
        "/ai/health-risk-score",
        payload,
        token,
    )

    passed = print_result(
        "/ai/health-risk-score",
        response,
    )

    results.append(
        (
            "Health Risk Score",
            "/ai/health-risk-score",
            passed,
        )
    )

    # ========================================================
    # 8. PATIENT SUMMARY
    # ========================================================

    print_section(8, "Patient Summary")

    payload = {
        "symptoms": [
            "fatigue",
            "frequent urination",
        ],
        "disease_risk": {
            "risk_score": 15,
            "risk_level": "Low",
        },
        "medical_report": {
            "severity": "Moderate",
            "abnormal_parameters": [
                "glucose",
                "cholesterol",
            ],
        },
        "prescription_analysis": {
            "safety_level": "Low",
            "warning_count": 0,
        },
        "triage_analysis": {
            "level": "Urgent",
        },
        "appointment_recommendation": {
            "department": "General Medicine",
            "specialty": "General Medicine",
        },
    }

    response = post_json(
        session,
        "/ai/patient-summary",
        payload,
        token,
    )

    passed = print_result(
        "/ai/patient-summary",
        response,
    )

    results.append(
        (
            "Patient Summary",
            "/ai/patient-summary",
            passed,
        )
    )

    # ========================================================
    # 9. MEDICAL CHAT ASSISTANT
    # ========================================================

    print_section(9, "Medical Chat Assistant")

    payload = {
        "message": (
            "I have fatigue and frequent urination. "
            "What general information should I know?"
        ),
        "context": {},
        "medical_context": {},
    }

    response = post_json(
        session,
        "/ai/medical-chat",
        payload,
        token,
    )

    passed = print_result(
        "/ai/medical-chat",
        response,
    )

    results.append(
        (
            "Medical Chat Assistant",
            "/ai/medical-chat",
            passed,
        )
    )

    # ========================================================
    # 10. CLINICAL DECISION SUPPORT
    # ========================================================

    print_section(10, "Clinical Decision Support")

    payload = {
        "symptoms": [
            "fatigue",
            "frequent urination",
        ],
        "diagnoses": [
            "possible diabetes",
        ],
        "medications": [
            "metformin",
        ],
        "lab_findings": [
            "high glucose",
            "high cholesterol",
        ],
        "prescription_analysis": {
            "warning_count": 0,
            "level": "Low",
        },
        "triage_analysis": {
            "level": "Urgent",
        },
        "appointment_recommendation": {
            "specialty": "General Medicine",
        },
    }

    response = post_json(
        session,
        "/ai/clinical-decision-support",
        payload,
        token,
    )

    passed = print_result(
        "/ai/clinical-decision-support",
        response,
    )

    results.append(
        (
            "Clinical Decision Support",
            "/ai/clinical-decision-support",
            passed,
        )
    )

    # ========================================================
    # 11. HOSPITAL ANALYTICS
    # ========================================================

    print_section(11, "Hospital Analytics")

    # IMPORTANT:
    # Do NOT use:
    # patient_count
    # admission_count
    # discharge_count
    # emergency_count
    # bed_count
    #
    # The backend expects the exact names below.

    payload = {
        "total_patients": 100,
        "total_doctors": 10,
        "total_appointments": 40,
        "total_admissions": 25,
        "total_discharges": 20,
        "total_emergency_cases": 10,
        "total_beds": 50,
        "occupied_beds": 35,
    }

    response = post_json(
        session,
        "/ai/hospital-analytics",
        payload,
        token,
    )

    passed = print_result(
        "/ai/hospital-analytics",
        response,
    )

    results.append(
        (
            "Hospital Analytics",
            "/ai/hospital-analytics",
            passed,
        )
    )

    # ========================================================
    # 12. RESOURCE PREDICTION
    # ========================================================

    print_section(12, "Resource Prediction")

    # IMPORTANT:
    # Backend requires:
    # current_patients
    # average_daily_admissions
    # average_daily_discharges
    # total_beds
    # occupied_beds
    #
    # The previous test incorrectly sent:
    # current_beds
    # doctors
    # nurses
    # emergency_cases

    payload = {
        "current_patients": 100,
        "average_daily_admissions": 20.0,
        "average_daily_discharges": 15.0,
        "total_beds": 50,
        "occupied_beds": 35,
        "prediction_days": 7,
    }

    response = post_json(
        session,
        "/ai/resource-prediction",
        payload,
        token,
    )

    passed = print_result(
        "/ai/resource-prediction",
        response,
    )

    results.append(
        (
            "Resource Prediction",
            "/ai/resource-prediction",
            passed,
        )
    )

    # ========================================================
    # 13. READMISSION RISK
    # ========================================================

    print_section(13, "Readmission Risk")

    # IMPORTANT:
    # previous_readmissions is required.

    payload = {
        "age": 65,
        "previous_admissions": 2,
        "previous_readmissions": 1,
        "length_of_stay": 7,
        "chronic_conditions": [
            "diabetes",
            "hypertension",
        ],
        "emergency_admission": False,
    }

    response = post_json(
        session,
        "/ai/readmission-risk",
        payload,
        token,
    )

    passed = print_result(
        "/ai/readmission-risk",
        response,
    )

    results.append(
        (
            "Readmission Risk",
            "/ai/readmission-risk",
            passed,
        )
    )

    # ========================================================
    # 14. DISCHARGE RISK
    # ========================================================

    print_section(14, "Discharge Risk")

    payload = {
        "age": 65,
        "length_of_stay": 7,
        "chronic_conditions": [
            "diabetes",
            "hypertension",
        ],
        "abnormal_lab_results": [
            "high glucose",
        ],
        "mobility_problem": False,
        "social_support": "adequate",
    }

    response = post_json(
        session,
        "/ai/discharge-risk",
        payload,
        token,
    )

    passed = print_result(
        "/ai/discharge-risk",
        response,
    )

    results.append(
        (
            "Discharge Risk",
            "/ai/discharge-risk",
            passed,
        )
    )

    # ========================================================
    # 15. CARE PLAN
    # ========================================================

    print_section(15, "Care Plan")

    payload = {
        "diagnoses": [
            "diabetes",
        ],
        "symptoms": [
            "fatigue",
            "frequent urination",
        ],
        "medications": [
            "metformin",
        ],
        "chronic_conditions": [
            "diabetes",
            "hypertension",
        ],
    }

    response = post_json(
        session,
        "/ai/care-plan",
        payload,
        token,
    )

    passed = print_result(
        "/ai/care-plan",
        response,
    )

    results.append(
        (
            "Care Plan",
            "/ai/care-plan",
            passed,
        )
    )

    # ========================================================
    # 16. PATIENT MONITORING
    # ========================================================

    print_section(16, "Patient Monitoring")

    # IMPORTANT:
    # The backend does NOT expect:
    #
    # {
    #     "patient_id": 1,
    #     "vital_signs": {
    #         ...
    #     }
    # }
    #
    # It expects the six vital signs directly in the body.

    payload = {
        "heart_rate": 85,
        "systolic_bp": 130,
        "diastolic_bp": 80,
        "temperature": 37.2,
        "oxygen_saturation": 97,
        "respiratory_rate": 16,
    }

    response = post_json(
        session,
        "/ai/patient-monitoring",
        payload,
        token,
    )

    passed = print_result(
        "/ai/patient-monitoring",
        response,
    )

    results.append(
        (
            "Patient Monitoring",
            "/ai/patient-monitoring",
            passed,
        )
    )

    # ========================================================
    # 17. PATIENT DETERIORATION
    # ========================================================

    print_section(17, "Patient Deterioration")

    # IMPORTANT:
    # Again, vital signs must be at the top level.
    #
    # Do NOT send:
    # "vital_signs": {...}

    payload = {
        "heart_rate": 110,
        "systolic_bp": 100,
        "oxygen_saturation": 92,
        "respiratory_rate": 24,
        "temperature": 38.5,
        "consciousness": "normal",
    }

    response = post_json(
        session,
        "/ai/patient-deterioration",
        payload,
        token,
    )

    passed = print_result(
        "/ai/patient-deterioration",
        response,
    )

    results.append(
        (
            "Patient Deterioration",
            "/ai/patient-deterioration",
            passed,
        )
    )

    # ========================================================
    # 18. MEDICATION ADHERENCE RISK
    # ========================================================

    print_section(18, "Medication Adherence Risk")

    # IMPORTANT:
    # previous_non_adherence is required.

    payload = {
        "missed_doses": 2,
        "total_doses": 14,
        "previous_non_adherence": 1,
        "side_effects": [],
        "cost_problem": False,
        "forgetfulness": True,
    }

    response = post_json(
        session,
        "/ai/medication-adherence-risk",
        payload,
        token,
    )

    passed = print_result(
        "/ai/medication-adherence-risk",
        response,
    )

    results.append(
        (
            "Medication Adherence Risk",
            "/ai/medication-adherence-risk",
            passed,
        )
    )

    # ========================================================
    # 19. APPOINTMENT NO-SHOW RISK
    # ========================================================

    print_section(19, "Appointment No-Show Risk")

    # IMPORTANT:
    # Backend requires:
    # previous_no_shows
    # previous_appointments
    # rescheduled_appointments
    # waiting_time_minutes
    # barriers
    # appointments_same_day
    # weekend_appointment

    payload = {
        "previous_no_shows": 1,
        "previous_appointments": 5,
        "rescheduled_appointments": 1,
        "waiting_time_minutes": 30,
        "barriers": [],
        "appointments_same_day": 1,
        "weekend_appointment": False,
    }

    response = post_json(
        session,
        "/ai/appointment-no-show-risk",
        payload,
        token,
    )

    passed = print_result(
        "/ai/appointment-no-show-risk",
        response,
    )

    results.append(
        (
            "Appointment No-Show Risk",
            "/ai/appointment-no-show-risk",
            passed,
        )
    )

    # ========================================================
    # 20. PATIENT FLOW PREDICTION
    # ========================================================

    print_section(20, "Patient Flow Prediction")

    # IMPORTANT:
    # Backend requires all of these:
    #
    # current_patients
    # average_daily_patients
    # current_admissions
    # average_daily_admissions
    # current_discharges
    # average_daily_discharges
    # current_emergency_cases
    # average_daily_emergency_cases
    # total_beds
    # occupied_beds
    # prediction_days

    payload = {
        "current_patients": 100,
        "average_daily_patients": 105.0,
        "current_admissions": 20,
        "average_daily_admissions": 18.0,
        "current_discharges": 15,
        "average_daily_discharges": 16.0,
        "current_emergency_cases": 8,
        "average_daily_emergency_cases": 7.0,
        "total_beds": 50,
        "occupied_beds": 35,
        "prediction_days": 7,
    }

    response = post_json(
        session,
        "/ai/patient-flow-prediction",
        payload,
        token,
    )

    passed = print_result(
        "/ai/patient-flow-prediction",
        response,
    )

    results.append(
        (
            "Patient Flow Prediction",
            "/ai/patient-flow-prediction",
            passed,
        )
    )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print_separator()
    print("FINAL AI TEST SUMMARY")
    print_separator()

    total = len(results)
    passed_count = sum(
        1 for _, _, passed in results if passed
    )
    failed_count = total - passed_count

    print()
    print(f"Total tests : {total}")
    print(f"Passed      : {passed_count}")
    print(f"Failed      : {failed_count}")

    print()
    print_separator()
    print("ENDPOINT RESULTS")
    print_separator()

    for index, (name, endpoint, passed) in enumerate(
        results,
        start=1,
    ):
        status = "PASS" if passed else "FAIL"

        print(
            f"{index:02d}. "
            f"{name:<35} "
            f"{status}"
        )

    print()
    print_separator()

    if failed_count == 0:
        print("ALL 20 AI ENDPOINTS PASSED")
    else:
        print(
            f"{failed_count} AI ENDPOINT(S) NEED ATTENTION"
        )

    print_separator()
    print()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()