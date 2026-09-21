import json
import os
from decimal import Decimal, InvalidOperation

from adapters.providers.postgres_product_repository import PostgresProductRepository
from domain.services.product_domain_service import ProductDomainService


db_url = os.environ.get("DB_URL", "")
product_service = ProductDomainService(
    product_repo=PostgresProductRepository(db_connection_string=db_url)
)


def handler(event, context):
    headers = {"Content-Type": "application/json"}

    try:
        body = json.loads(event.get("body") or "{}")
        if not isinstance(body, dict):
            raise ValueError("El cuerpo debe ser un objeto JSON.")

        name = body.get("name")
        if not isinstance(name, str):
            raise ValueError("El nombre es obligatorio.")

        try:
            price = Decimal(str(body.get("price")))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("El precio debe ser numérico.")

        description = body.get("description")
        if description is not None and not isinstance(description, str):
            raise ValueError("La descripción debe ser texto.")

        is_available = body.get("is_available", True)
        if not isinstance(is_available, bool):
            raise ValueError("is_available debe ser booleano.")

        product = product_service.create_product(
            name=name,
            description=description,
            price=price,
            is_available=is_available,
        )
        return {
            "statusCode": 201,
            "headers": headers,
            "body": json.dumps(product.to_dict()),
        }
    except (ValueError, json.JSONDecodeError) as error:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": str(error)}),
        }
    except Exception:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Internal Server Error"}),
        }
