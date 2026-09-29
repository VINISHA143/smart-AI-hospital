from pwdlib import PasswordHash

from app.database import SessionLocal
from app.models.user import User

password_hash = PasswordHash.recommended()

db = SessionLocal()

try:
    username = "admin"
    password = "Admin@123"
    role = "Admin"

    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    if user:
        user.password_hash = password_hash.hash(password)
        user.role = role
        user.is_active = True

        db.commit()

        print("Admin user updated successfully")
    else:
        user = User(
            username=username,
            password_hash=password_hash.hash(password),
            role=role,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print("Admin user created successfully")

    print("Username: admin")
    print("Password: Admin@123")
    print("Role: Admin")

except Exception as e:
    db.rollback()
    print("ERROR:", e)

finally:
    db.close()