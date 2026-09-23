import psycopg
from decimal import Decimal
from typing import Optional
from uuid import UUID

from domain.entities.product import Product
from ports.product_repository_port import ProductRepositoryPort


class PostgresProductRepository(ProductRepositoryPort):
    def __init__(self, db_connection_string: str):
        self.db_url = db_connection_string
        self._ensure_table()

    def _ensure_table(self) -> None:
        if not self.db_url:
            raise ValueError("DB_URL no está configurada.")

        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS products (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(100) NOT NULL,
                        description TEXT,
                        price NUMERIC(10, 2) NOT NULL,
                        is_available BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        path VARCHAR(100)
                    )
                    """
                )
                conn.commit()

    def create(
        self,
        name: str,
        description: Optional[str],
        price: Decimal,
        is_available: bool,
        path: str,
    ) -> Product:
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO products (name, description, price, is_available, path)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, name, description, price, is_available, created_at, path
                    """,
                    (name, description, price, is_available, path),
                )
                row = cur.fetchone()
                conn.commit()
                return Product(
                    id=UUID(str(row[0])),
                    name=row[1],
                    description=row[2],
                    price=row[3],
                    is_available=row[4],
                    created_at=row[5],
                    path=row[6],
                )

    @staticmethod
    def _to_product(row) -> Product:
        return Product(
            id=UUID(str(row[0])),
            name=row[1],
            description=row[2],
            price=row[3],
            is_available=row[4],
            created_at=row[5],
            path=row[6],
        )

    def find_all(self) -> list[Product]:
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, description, price, is_available, created_at, path "
                    "FROM products ORDER BY created_at DESC"
                )
                return [self._to_product(row) for row in cur.fetchall()]

    def find_by_id(self, product_id: UUID) -> Optional[Product]:
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, description, price, is_available, created_at, path "
                    "FROM products WHERE id = %s",
                    (product_id,),
                )
                row = cur.fetchone()
                return self._to_product(row) if row else None

    def update(self, product_id: UUID, fields: dict) -> Optional[Product]:
        assignments = ", ".join(f"{field} = %s" for field in fields)
        values = list(fields.values()) + [product_id]
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"UPDATE products SET {assignments} WHERE id = %s "
                    "RETURNING id, name, description, price, is_available, created_at, path",
                    values,
                )
                row = cur.fetchone()
                conn.commit()
                return self._to_product(row) if row else None

    def delete(self, product_id: UUID) -> bool:
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted
