from typing import Dict, Any
from ports.user_repository_port import UserRepositoryPort
from ports.token_provider_port import TokenProviderPort
from domain.entities.user import User
from domain.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotFoundException,
)
from ports.token_revocation_port import TokenRevocationPort

class UserDomainService:
    def __init__(
        self,
        user_repo: UserRepositoryPort,
        token_provider: TokenProviderPort,
        token_revocation_store: TokenRevocationPort = None,
    ):
        self.user_repo = user_repo
        self.token_provider = token_provider
        self.token_revocation_store = token_revocation_store

    def list_users(self) -> list[dict]:
        return [user.to_dict() for user in self.user_repo.find_all()]

    def get_current_user(self, token: str) -> dict:
        if self.token_revocation_store and self.token_revocation_store.is_revoked(token):
            raise ValueError("El token fue revocado.")

        payload = self.token_provider.decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("El token no contiene un usuario válido.")

        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundException("Usuario no encontrado.")
        return user.to_dict()

    def logout(self, token: str) -> None:
        payload = self.token_provider.decode_token(token)
        expires_at = payload.get("exp")
        if not expires_at or not self.token_revocation_store:
            raise ValueError("El token no puede ser revocado.")
        self.token_revocation_store.revoke(token, int(expires_at))

    def update_user(self, user_id: str, fields: dict) -> dict:
        current_user = self.user_repo.find_by_id(user_id)
        if not current_user:
            raise UserNotFoundException("Usuario no encontrado.")

        updates = {key: value for key, value in fields.items() if value is not None}
        for field in ("name", "phone", "email", "role"):
            if field in updates and not isinstance(updates[field], str):
                raise ValueError(f"El campo {field} debe ser texto.")

        if "phone" in updates:
            existing_user = self.user_repo.find_by_phone(updates["phone"])
            if existing_user and existing_user.id != user_id:
                raise UserAlreadyExistsException("El número de teléfono ya se encuentra registrado.")

        if "email" in updates:
            existing_user = self.user_repo.find_by_email(updates["email"])
            if existing_user and existing_user.id != user_id:
                raise UserAlreadyExistsException("El correo electrónico ya se encuentra registrado.")

        if "password" in updates:
            password = updates.pop("password")
            if not isinstance(password, str) or not password:
                raise ValueError("El campo password debe ser un texto no vacío.")
            updates["password_hash"] = self.token_provider.hash_password(password)

        if not updates:
            raise ValueError("Debe enviar al menos un campo para actualizar.")

        updated_user = self.user_repo.update(user_id, updates)
        if not updated_user:
            raise UserNotFoundException("Usuario no encontrado.")
        return updated_user.to_dict()

    def delete_user(self, user_id: str) -> None:
        if not self.user_repo.delete(user_id):
            raise UserNotFoundException("Usuario no encontrado.")

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