from abc import ABC, abstractmethod

class TokenProviderPort(ABC):

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Genera un hash seguro de la contraseña."""
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña en texto plano contra su hash."""
        pass

    @abstractmethod
    def generate_token(self, payload: dict) -> str:
        """Genera un JWT firmado con el payload del usuario."""
        pass

    @abstractmethod
    def decode_token(self, token: str) -> dict:
        """Valida y decodifica un JWT."""
        pass