from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID


class Product:
    def __init__(
        self,
        id: UUID,
        name: str,
        description: Optional[str],
        price: Decimal,
        is_available: bool,
        created_at: datetime,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.is_available = is_available
        self.created_at = created_at

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat(),
        }
