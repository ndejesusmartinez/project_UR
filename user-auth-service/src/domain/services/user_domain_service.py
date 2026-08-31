from typing import Dict, Any
from ports.user_repository_port import UserRepositoryPort
from ports.token_provider_port import TokenProviderPort
from domain.entities.user import User
from domain.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
)

class UserDomainService:
    def __init__(self, user_repo: UserRepositoryPort, token_provider: TokenProviderPort):
        self.user_repo = user_repo
        self.token_provider = token_provider

    def register_user(self, name: str, phone: str, email: str, raw_password: str, role: str = "CLIENT") -> dict:
        # 1. Regla: El teléfono no puede estar duplicado
        existing_user = self.user_repo.find_by_phone(phone)
        if existing_user:
            raise UserAlreadyExistsException(f"El número {phone} ya se encuentra registrado.")

        # 2. Hash de contraseña
        hashed_password = self.token_provider.hash_password(raw_password)

        # 3. Crear entidad y guardar
        new_user = User.create(name=name, phone=phone, email=email, role=role, password_hash=hashed_password)
        saved_user = self.user_repo.save(new_user)

        # 4. Emitir token
        token = self.token_provider.generate_token({"sub": saved_user.id, "role": saved_user.role})

        return {
            "user": saved_user.to_dict(),
            "access_token": token
        }

    def authenticate_user(self, phone: str, email: str, raw_password: str) -> dict:
        user = self.user_repo.find_by_phone(phone)
        if not user or not user.password_hash or user.email != email:
            raise InvalidCredentialsException("Credenciales inválidas.")

        if not self.token_provider.verify_password(raw_password, user.password_hash):
            raise InvalidCredentialsException("Credenciales inválidas.")

        token = self.token_provider.generate_token({"sub": user.id, "role": user.role})

        return {
            "user": user.to_dict(),
            "access_token": token
        }