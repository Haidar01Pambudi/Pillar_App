import getpass
import sys

from sqlalchemy import func, select

import app.models
from app.core.permissions import Role
from app.core.security import hash_password
from app.db import SessionLocal
from app.modules.auth.models import User
from app.modules.lookups.service import seed_defaults

def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python -, scripts.create_admin <username> "<Full name>"')
        return 1
    username = sys.argv[1].strip().lower()
    full_name = sys.argv[2] if len(sys.argv) > 2 else username
    password = getpass.getpass("Password: ")
    if len(password) < 10 or password != getpass.getpass("Repeat: "):
        print("Minimum 10 characters, must match.")
        return 1
    with SessionLocal() as db:
        seeded = seed_defaults(db)
        u = db.scalar(select(User).where(func.lower(User.username) == username))
        if u:
            u.password_hash, u.role, u.is_active = hash_password(password), Role.ADMIN.value, True
            print(f"Updated admin '{username}'.")
        else:
            db.add(
                User(
                    username=username,
                    full_name=full_name,
                    role=Role.ADMIN.value,
                    password_hash=hash_password(password),
                    is_active=True,
                )
            )
            print(f"Created Admin '{username}'.")
        db.commit()
    print(f"Seeded {seeded} default list values.")
    return 0

if __name__ == "__main__":
    sys.exit(main())