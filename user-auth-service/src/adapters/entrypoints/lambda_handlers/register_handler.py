import json
import os
from adapters.providers.postgres_user_repository import PostgresUserRepository
from adapters.providers.jwt_token_provider import JwtTokenProvider
from domain.services.user_domain_service import UserDomainService
from domain.exceptions.user_exceptions import UserAlreadyExistsException

# Reutilización de conexiones fuera del handler (Cold Starts optimizados)
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
        
        name = body.get("name")
        phone = body.get("phone")
        password = body.get("password")
        role = body.get("role", "CLIENT")
        email = body.get("email")

        if not name or not phone or not password or not email:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"error": "Faltan campos obligatorios (name, phone, password, email)"})
            }

        result = user_service.register_user(
            name=name,
            phone=phone,
            raw_password=password,
            role=role,
            email=email
        )

        return {
            "statusCode": 201,
            "headers": headers,
            "body": json.dumps(result)
        }

    except UserAlreadyExistsException as e:
        return {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)})
        }