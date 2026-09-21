import json
import os
from uuid import UUID

from adapters.providers.postgres_product_repository import PostgresProductRepository
from domain.exceptions.product_exceptions import ProductNotFoundException
from domain.services.product_domain_service import ProductDomainService


product_service = ProductDomainService(
    product_repo=PostgresProductRepository(os.environ.get("DB_URL", ""))
)


def handler(event, context):
    product_id = (event.get("pathParameters") or {}).get("product_id")
    try:
        product = product_service.get_product(UUID(product_id))
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(product.to_dict()),
        }
    except (ValueError, TypeError, AttributeError):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "El product_id no es un UUID válido."}),
        }
    except ProductNotFoundException as error:
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(error)}),
        }
    except Exception:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal Server Error"}),
        }
