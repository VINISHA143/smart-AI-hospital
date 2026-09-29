from pwdlib import PasswordHash

from app.database import SessionLocal
from app.models.user import User

password_hash = PasswordHash.recommended()

db = SessionLocal()

test_users = [
    {
        "username": "doctor",
        "password": "Doctor@123",
        "role": "Doctor",
    },
    {
        "username": "receptionist",
        "password": "Reception@123",
        "role": "Receptionist",
    },
    {
        "username": "pharmacy",
        "password": "Pharmacy@123",
        "role": "Pharmacy",
    },
]

try:
    for data in test_users:
        user = (
            db.query(User)
            .filter(User.username == data["username"])
            .first()
        )

        hashed_password = password_hash.hash(data["password"])

        if user:
            user.password_hash = hashed_password
            user.role = data["role"]
            user.is_active = True
            print(f"Updated: {data['username']}")
        else:
            user = User(
                username=data["username"],
                password_hash=hashed_password,
                role=data["role"],
                is_active=True,
            )

            db.add(user)
            print(f"Created: {data['username']}")

    db.commit()

    print("\nTest users ready:")
    print("doctor       / Doctor@123")
    print("receptionist / Reception@123")
    print("pharmacy     / Pharmacy@123")

except Exception as e:
    db.rollback()
    print("ERROR:", e)

finally:
    db.close()