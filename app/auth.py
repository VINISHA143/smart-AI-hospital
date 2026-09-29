from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError


# =========================
# JWT CONFIGURATION
# =========================

SECRET_KEY = "smart-hospital-secret-key-change-later"
ALGORITHM = "HS256"


# =========================
# BEARER AUTHENTICATION
# =========================

security = HTTPBearer()


# =========================
# ROLE PERMISSIONS
# =========================

ROLE_PERMISSIONS = {
    "Admin": [
        "users",
        "patients",
        "doctors",
        "appointments",
        "admissions",
        "medical_records",
        "prescriptions",
        "lab_reports",
        "medicines",
        "billing",
        "wards",
        "beds",
        "emergency_cases",
    ],

    "Doctor": [
        "patients",
        "doctors",
        "appointments",
        "admissions",
        "medical_records",
        "prescriptions",
        "lab_reports",
        "emergency_cases",
    ],

    "Receptionist": [
        "patients",
        "doctors",
        "appointments",
        "admissions",
        "billing",
    ],

    "Pharmacy": [
        "patients",
        "prescriptions",
        "medicines",
        "lab_reports",
    ],
}


# =========================
# GET CURRENT USER
# =========================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")
        role = payload.get("role")

        if not username or not role:
            raise credentials_exception

        return {
            "username": username,
            "role": role,
        }

    except JWTError:
        raise credentials_exception


# =========================
# ROLE CHECK
# =========================

def require_role(*allowed_roles):
    def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return role_checker


# =========================
# PERMISSION CHECK
# =========================

def require_permission(permission: str):
    def permission_checker(
        current_user: dict = Depends(get_current_user)
    ):
        role = current_user["role"]

        permissions = ROLE_PERMISSIONS.get(role, [])

        if permission not in permissions:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource",
            )

        return current_user

    return permission_checker