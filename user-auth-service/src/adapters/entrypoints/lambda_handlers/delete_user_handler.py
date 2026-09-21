import json
import os

from adapters.providers.jwt_token_provider import JwtTokenProvider
from adapters.providers.postgres_user_repository import PostgresUserRepository
from domain.exceptions.user_exceptions import UserNotFoundException
from domain.services.user_domain_service import UserDomainService

db_url = os.environ.get("DB_URL", "")
jwt_secret = os.environ.get("JWT_SECRET", "super_secret_key")

user_repo = PostgresUserRepository(db_connection_string=db_url)
token_provider = JwtTokenProvider(secret=jwt_secret)
user_service = UserDomainService(user_repo=user_repo, token_provider=token_provider)


def handler(event, context):
    headers = {"Content-Type": "application/json"}
    user_id = (event.get("pathParameters") or {}).get("user_id")

    try:
        user_service.delete_user(user_id)
        return {"statusCode": 204, "headers": headers, "body": ""}
    except UserNotFoundException as error:
        return {"statusCode": 404, "headers": headers, "body": json.dumps({"error": str(error)})}
    except Exception:
        return {"statusCode": 500, "headers": headers, "body": json.dumps({"error": "Internal Server Error"})}