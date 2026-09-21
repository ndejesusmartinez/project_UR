import json
import os

from adapters.providers.postgres_product_repository import PostgresProductRepository
from domain.services.product_domain_service import ProductDomainService


product_service = ProductDomainService(
    product_repo=PostgresProductRepository(os.environ.get("DB_URL", ""))
)


def handler(event, context):
    try:
        products = [product.to_dict() for product in product_service.list_products()]
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(products),
        }
    except Exception:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal Server Error"}),
        }
