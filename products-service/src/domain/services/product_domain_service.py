from decimal import Decimal
from typing import Optional
from uuid import UUID

from domain.entities.product import Product
from domain.exceptions.product_exceptions import ProductNotFoundException
from ports.product_repository_port import ProductRepositoryPort


class ProductDomainService:
    def __init__(self, product_repo: ProductRepositoryPort):
        self.product_repo = product_repo

    def create_product(
        self,
        name: str,
        path: str,
        description: Optional[str],
        price: Decimal,
        is_available: bool = True,
    ) -> Product:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("El nombre es obligatorio.")
        if len(normalized_name) > 100:
            raise ValueError("El nombre no puede superar los 100 caracteres.")
        if price < 0:
            raise ValueError("El precio no puede ser negativo.")

        return self.product_repo.create(
            name=normalized_name,
            description=description,
            price=price,
            is_available=is_available,
            path=path,
        )

    def list_products(self) -> list[Product]:
        return self.product_repo.find_all()

    def get_product(self, product_id: UUID) -> Product:
        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise ProductNotFoundException("Producto no encontrado.")
        return product

    def update_product(self, product_id: UUID, fields: dict) -> Product:
        updates = {key: value for key, value in fields.items() if value is not None}
        allowed_fields = {"name", "description", "price", "is_available"}
        if not updates or any(key not in allowed_fields for key in updates):
            raise ValueError("Debe enviar al menos un campo válido para actualizar.")

        if "name" in updates:
            if not isinstance(updates["name"], str) or not updates["name"].strip():
                raise ValueError("El nombre es obligatorio.")
            updates["name"] = updates["name"].strip()
            if len(updates["name"]) > 100:
                raise ValueError("El nombre no puede superar los 100 caracteres.")
        if "description" in updates and not isinstance(updates["description"], str):
            raise ValueError("La descripción debe ser texto.")
        if "price" in updates and updates["price"] < 0:
            raise ValueError("El precio no puede ser negativo.")
        if "is_available" in updates and not isinstance(updates["is_available"], bool):
            raise ValueError("is_available debe ser booleano.")

        product = self.product_repo.update(product_id, updates)
        if not product:
            raise ProductNotFoundException("Producto no encontrado.")
        return product

    def delete_product(self, product_id: UUID) -> None:
        if not self.product_repo.delete(product_id):
            raise ProductNotFoundException("Producto no encontrado.")
