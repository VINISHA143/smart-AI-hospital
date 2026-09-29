from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from pwdlib import PasswordHash
from jose import jwt

from app.database import SessionLocal
from app.models.user import User
from app.auth import SECRET_KEY, ALGORITHM


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


password_hash = PasswordHash.recommended()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.username == login_data.username)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    password_valid = False

    try:
        password_valid = password_hash.verify(
            login_data.password,
            user.password_hash
        )

    except Exception:
        password_valid = False

    # Temporary migration for old plaintext passwords
    if (
        not password_valid
        and user.password_hash == login_data.password
    ):
        user.password_hash = password_hash.hash(
            login_data.password
        )

        db.commit()
        db.refresh(user)

        password_valid = True

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    token_data = {
        "sub": user.username,
        "role": user.role
    }

    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }