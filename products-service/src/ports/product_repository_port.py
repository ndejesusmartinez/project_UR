from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from uuid import UUID

from domain.entities.product import Product


class ProductRepositoryPort(ABC):

    @abstractmethod
    def create(
        self,
        name: str,
        description: Optional[str],
        price: Decimal,
        is_available: bool,
        path: str,
    ) -> Product:
        pass

    @abstractmethod
    def find_all(self) -> list[Product]:
        pass

    @abstractmethod
    def find_by_id(self, product_id: UUID) -> Optional[Product]:
        pass

    @abstractmethod
    def update(self, product_id: UUID, fields: dict) -> Optional[Product]:
        pass

    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        pass
