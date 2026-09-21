from abc import ABC, abstractmethod


class TokenRevocationPort(ABC):

    @abstractmethod
    def revoke(self, token: str, expires_at: int) -> None:
        """Revoca un token hasta su fecha de expiración."""
        pass

    @abstractmethod
    def is_revoked(self, token: str) -> bool:
        """Comprueba si un token fue revocado."""
        pass