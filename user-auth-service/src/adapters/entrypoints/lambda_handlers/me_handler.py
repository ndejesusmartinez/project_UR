import json
import os

from adapters.providers.jwt_token_provider import JwtTokenProvider
from adapters.providers.postgres_user_repository import PostgresUserRepository
from adapters.providers.postgres_token_revocation_store import PostgresTokenRevocationStore
from domain.exceptions.user_exceptions import UserNotFoundException
from domain.services.user_domain_service import UserDomainService

db_url = os.environ.get("DB_URL", "")
jwt_secret = os.environ.get("JWT_SECRET", "super_secret_key")

user_repo = PostgresUserRepository(db_connection_string=db_url)
token_provider = JwtTokenProvider(secret=jwt_secret)
token_revocation_store = PostgresTokenRevocationStore(db_connection_string=db_url)
user_service = UserDomainService(
    user_repo=user_repo,
    token_provider=token_provider,
    token_revocation_store=token_revocation_store
)


def handler(event, context):
    headers = {"Content-Type": "application/json"}
    request_headers = event.get("headers") or {}
    authorization = request_headers.get("authorization") or request_headers.get("Authorization")

    if not authorization or not authorization.startswith("Bearer "):
        return {
            "statusCode": 401,
            "headers": headers,
            "body": json.dumps({"error": "Se requiere un token Bearer."})
        }

    try:
        user = user_service.get_current_user(authorization[7:].strip())
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(user)
        }
    except UserNotFoundException as error:
        return {
            "statusCode": 404,
            "headers": headers,
            "body": json.dumps({"error": str(error)})
        }
    except Exception:
        return {
            "statusCode": 401,
            "headers": headers,
            "body": json.dumps({"error": "Token inválido o expirado."})
        }