import json
import os
from adapters.providers.postgres_user_repository import PostgresUserRepository
from adapters.providers.jwt_token_provider import JwtTokenProvider
from domain.services.user_domain_service import UserDomainService
from domain.exceptions.user_exceptions import InvalidCredentialsException

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
        body = json.loads(event.get("body", "{}"))
        password = body.get("password")
        email = body.get("email")

        if not email or not password:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Debe enviar email y password"})
            }

        result = user_service.authenticate_user(
            email=email,
            raw_password=password
        )

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(result)
        }

    except InvalidCredentialsException as e:
        return {
            "statusCode": 401,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)})
        }