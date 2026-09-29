from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, Field
from pwdlib import PasswordHash

from app.database import SessionLocal
from app.models.user import User
from app.auth import require_permission


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

password_hash = PasswordHash.recommended()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    role: str = Field(min_length=1, max_length=50)


# =========================
# GET ALL USERS
# =========================

@router.get("/")
def get_users(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("users"))
):
    return db.query(User).all()


# =========================
# GET USER BY ID
# =========================

@router.get("/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("users"))
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


# =========================
# CREATE USER
# =========================

@router.post("/")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("users"))
):
    existing_user = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    new_user = User(
        username=user.username,
        password_hash=password_hash.hash(user.password),
        role=user.role,
        is_active=True
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="User could not be created because of a database conflict"
        )


# =========================
# UPDATE USER
# =========================

@router.put("/{user_id}")
def update_user(
    user_id: int,
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("users"))
):
    existing_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    duplicate_user = (
        db.query(User)
        .filter(
            User.username == user.username,
            User.id != user_id
        )
        .first()
    )

    if duplicate_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists"
        )

    existing_user.username = user.username
    existing_user.password_hash = password_hash.hash(user.password)
    existing_user.role = user.role

    try:
        db.commit()
        db.refresh(existing_user)

        return existing_user

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="User could not be updated because of a database conflict"
        )


# =========================
# DELETE USER
# =========================

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("users"))
):
    existing_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Prevent deleting the currently logged-in user
    if existing_user.username == current_user["username"]:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete the currently logged-in user"
        )

    try:
        db.delete(existing_user)
        db.commit()

        return {
            "message": "User deleted successfully",
            "user_id": user_id
        }

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="User cannot be deleted because related records exist"
        )