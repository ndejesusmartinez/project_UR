import json
import os
from decimal import Decimal, InvalidOperation
from uuid import UUID

from adapters.providers.postgres_product_repository import PostgresProductRepository
from domain.exceptions.product_exceptions import ProductNotFoundException
from domain.services.product_domain_service import ProductDomainService


product_service = ProductDomainService(
    product_repo=PostgresProductRepository(os.environ.get("DB_URL", ""))
)


def _headers():
    return {"Content-Type": "application/json"}


def _parse_update_body(event):
    body = json.loads(event.get("body") or "{}")
    if not isinstance(body, dict):
        raise ValueError("El cuerpo debe ser un objeto JSON.")
    if "price" in body:
        try:
            body["price"] = Decimal(str(body["price"]))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("El precio debe ser numérico.")
    return body


def handler(event, context):
    headers = _headers()
    product_id = (event.get("pathParameters") or {}).get("product_id")
    try:
        product_uuid = UUID(product_id)
        method = (event.get("requestContext") or {}).get("http", {}).get("method", "").upper()
        if method == "DELETE":
            product_service.delete_product(product_uuid)
            return {"statusCode": 204, "headers": headers, "body": ""}

        product = product_service.update_product(product_uuid, _parse_update_body(event))
        return {"statusCode": 200, "headers": headers, "body": json.dumps(product.to_dict())}
    except ValueError as error:
        return {"statusCode": 400, "headers": headers, "body": json.dumps({"error": str(error)})}
    except ProductNotFoundException as error:
        return {"statusCode": 404, "headers": headers, "body": json.dumps({"error": str(error)})}
    except Exception:
        return {"statusCode": 500, "headers": headers, "body": json.dumps({"error": "Internal Server Error"})}
