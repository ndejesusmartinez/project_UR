import uuid
from datetime import datetime
from typing import Optional

class User:
    def __init__(
        self, 
        id: str, 
        name: str, 
        phone: str, 
        email: str,
        role: str = "CLIENT", 
        password_hash: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.phone = phone
        self.role = role
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.email = email

    @classmethod
    def create(cls, name: str, phone: str, email: str, role: str = "CLIENT", password_hash: Optional[str] = None) -> "User":
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            phone=phone,
            email=email,
            role=role,
            password_hash=password_hash
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else str(self.created_at)
        }