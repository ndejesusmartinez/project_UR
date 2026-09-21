import json
import os

from adapters.providers.jwt_token_provider import JwtTokenProvider
from adapters.providers.postgres_user_repository import PostgresUserRepository
from adapters.providers.postgres_token_revocation_store import PostgresTokenRevocationStore
from domain.services.user_domain_service import UserDomainService

db_url = os.environ.get("DB_URL", "")
jwt_secret = os.environ.get("JWT_SECRET", "super_secret_key")

user_service = UserDomainService(
    user_repo=PostgresUserRepository(db_connection_string=db_url),
    token_provider=JwtTokenProvider(secret=jwt_secret),
    token_revocation_store=PostgresTokenRevocationStore(db_connection_string=db_url)
)


def handler(event, context):
    headers = {"Content-Type": "application/json"}
    request_headers = event.get("headers") or {}
    authorization = request_headers.get("authorization") or request_headers.get("Authorization")

    if not authorization or not authorization.startswith("Bearer "):
        return {"statusCode": 401, "headers": headers, "body": json.dumps({"error": "Se requiere un token Bearer."})}

    try:
        user_service.logout(authorization[7:].strip())
        return {"statusCode": 204, "headers": headers, "body": ""}
    except Exception:
        return {"statusCode": 401, "headers": headers, "body": json.dumps({"error": "Token inválido o expirado."})}