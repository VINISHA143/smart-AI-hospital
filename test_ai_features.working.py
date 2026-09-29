import requests
import sys
import json

# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "http://127.0.0.1:8000"

USERNAME = "admin"

# IMPORTANT:
# Replace this with the password you use successfully
# for the admin account in Swagger /auth/login.
PASSWORD = "Admin@123"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_separator():
    print("\n" + "=" * 60)


def print_json(data):
    try:
        print(json.dumps(data, indent=2))
    except Exception:
        print(data)


# ============================================================
# STEP 1 - LOGIN
# ============================================================

def login():
    print_separator()
    print("AUTHENTICATION")
    print_separator()

    login_url = f"{BASE_URL}/auth/login"

    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        response = requests.post(
            login_url,
            json=login_data,
            timeout=10
        )
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to FastAPI server.")
        print("Make sure Terminal 1 is running:")
        print()
        print("python -m uvicorn app.main:app --reload")
        sys.exit(1)

    print("Login status:", response.status_code)

    try:
        response_data = response.json()
        print_json(response_data)
    except Exception:
        print(response.text)
        response_data = {}

    if response.status_code != 200:
        print()
        print("LOGIN FAILED")
        print("Check your admin username/password.")
        sys.exit(1)

    # Support several common token response formats.
    token = (
        response_data.get("access_token")
        or response_data.get("token")
    )

    # Some APIs return:
    # {
    #   "result": {
    #       "access_token": "..."
    #   }
    # }
    if not token and isinstance(response_data.get("result"), dict):
        token = (
            response_data["result"].get("access_token")
            or response_data["result"].get("token")
        )

    if not token:
        print()
        print("LOGIN SUCCEEDED, BUT NO ACCESS TOKEN WAS FOUND.")
        print()
        print("Your login response above shows the actual response format.")
        print("We need to use that token field in the test script.")
        sys.exit(1)

    print()
    print("LOGIN SUCCESSFUL")
    print("JWT token received.")

    return token


# ============================================================
# GENERIC AI REQUEST
# ============================================================

def call_ai_endpoint(
    number,
    name,
    endpoint,
    payload,
    token
):
    print_separator()
    print(f"{number}. {name}")
    print(f"POST {BASE_URL}{endpoint}")
    print_separator()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            json=payload,
            headers=headers,
            timeout=30
        )

    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server.")
        return

    except requests.exceptions.Timeout:
        print("ERROR: Request timed out.")
        return

    except Exception as exc:
        print("ERROR:", exc)
        return

    print("Status:", response.status_code)

    try:
        response_data = response.json()
        print_json(response_data)
    except Exception:
        print(response.text)

    if response.status_code == 401:
        print()
        print("AUTHENTICATION ERROR")
        print("The JWT token was rejected by the backend.")

    elif response.status_code == 422:
        print()
        print("VALIDATION ERROR")
        print("The endpoint is running, but the JSON fields do not")
        print("match the FastAPI request model.")

    elif response.status_code == 500:
        print()
        print("SERVER ERROR")
        print("The endpoint was reached, but backend code raised")
        print("an internal exception.")

    elif response.status_code == 200:
        print()
        print("SUCCESS")


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("SMART HOSPITAL AI - AI ENDPOINT TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    token = login()

    # --------------------------------------------------------
    # TEST DATA
    #
    # IMPORTANT:
    # These payloads are examples.
    # If your FastAPI schemas use different field names,
    # the endpoint will return 422 and we will correct that
    # endpoint from its OpenAPI schema.
    # --------------------------------------------------------

    symptom_analyzer_payload = {
        "symptoms": [
            "fatigue",
            "frequent urination"
        ],
        "age": 45,
        "gender": "male"
    }

    disease_risk_payload = {
        "age": 45,
        "gender": "male",
        "symptoms": [
            "fatigue",
            "frequent urination"
        ],
        "chronic_conditions": [
            "diabetes",
            "hypertension"
        ],
        "family_history": []
    }

    medical_report_payload = {
        "report_text": (
            "Glucose: 180 mg/dL. "
            "Blood pressure: 150/95 mmHg. "
            "Cholesterol: elevated."
        )
    }

    prescription_safety_payload = {
        "medications": [
            "metformin"
        ],
        "age": 45,
        "allergies": [],
        "chronic_conditions": [
            "diabetes"
        ]
    }

    emergency_triage_payload = {
    "symptoms": [
        "chest pain",
        "shortness of breath"
    ],
    "severity": 3,
    "age": 55,
    "heart_rate": 110,
    "systolic_bp": 150,
    "oxygen_saturation": 94
}

    appointment_recommendation_payload = {
        "symptoms": [
            "fatigue",
            "frequent urination"
        ],
        "age": 45,
        "chronic_conditions": [
            "diabetes"
        ]
    }

    health_risk_score_payload = {
        "age": 45,
        "smoking": False,
        "alcohol_use": False,
        "exercise": True,
        "chronic_conditions": [
            "diabetes",
            "hypertension"
        ],
        "family_history": []
    }

    patient_summary_payload = {
        "patient_name": "Test Patient",
        "age": 45,
        "gender": "male",
        "diagnoses": [
            "diabetes",
            "hypertension"
        ],
        "symptoms": [
            "fatigue",
            "frequent urination"
        ],
        "medications": [
            "metformin"
        ]
    }

    # --------------------------------------------------------
    # AI ENDPOINTS
    # --------------------------------------------------------

    call_ai_endpoint(
        1,
        "Symptom Analyzer",
        "/ai/symptom-analyzer",
        symptom_analyzer_payload,
        token
    )

    call_ai_endpoint(
        2,
        "Disease Risk",
        "/ai/disease-risk",
        disease_risk_payload,
        token
    )

    call_ai_endpoint(
        3,
        "Medical Report Analyzer",
        "/ai/medical-report-analyzer",
        medical_report_payload,
        token
    )

    call_ai_endpoint(
        4,
        "Prescription Safety",
        "/ai/prescription-safety",
        prescription_safety_payload,
        token
    )

    call_ai_endpoint(
        5,
        "Emergency Triage",
        "/ai/emergency-triage",
        emergency_triage_payload,
        token
    )

    call_ai_endpoint(
        6,
        "Appointment Recommendation",
        "/ai/appointment-recommendation",
        appointment_recommendation_payload,
        token
    )

    call_ai_endpoint(
        7,
        "Health Risk Score",
        "/ai/health-risk-score",
        health_risk_score_payload,
        token
    )

    call_ai_endpoint(
        8,
        "Patient Summary",
        "/ai/patient-summary",
        patient_summary_payload,
        token
    )

    # --------------------------------------------------------
    # FINISHED
    # --------------------------------------------------------

    print_separator()
    print("FIRST 8 AI ENDPOINT TESTS COMPLETED")
    print_separator()


if __name__ == "__main__":
    main()