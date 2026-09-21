import json
import os

from adapters.providers.postgres_user_repository import PostgresUserRepository
from adapters.providers.jwt_token_provider import JwtTokenProvider
from domain.services.user_domain_service import UserDomainService

db_url = os.environ.get("DB_URL", "")
jwt_secret = os.environ.get("JWT_SECRET", "super_secret_key")

user_repo = PostgresUserRepository(db_connection_string=db_url)
token_provider = JwtTokenProvider(secret=jwt_secret)
user_service = UserDomainService(user_repo=user_repo, token_provider=token_provider)


def handler(event, context):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }

    try:
        users = user_service.list_users()
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(users)
        }
    except Exception:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Internal Server Error"})
        }