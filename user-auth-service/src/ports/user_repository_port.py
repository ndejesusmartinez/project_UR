from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.user import User

class UserRepositoryPort(ABC):

    @abstractmethod
    def save(self, user: User) -> User:
        """Guarda un usuario en la persistencia."""
        pass

    @abstractmethod
    def find_by_phone(self, phone: str) -> Optional[User]:
        """Busca un usuario por su número de teléfono."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por su correo electrónico."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Busca un usuario por su UUID."""
        pass

    @abstractmethod
    def find_all(self) -> list[User]:
        """Lista todos los usuarios."""
        pass

    @abstractmethod
    def update(self, user_id: str, fields: dict) -> Optional[User]:
        """Actualiza los campos permitidos de un usuario."""
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Elimina un usuario por su UUID."""
        pass