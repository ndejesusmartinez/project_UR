import hashlib

import psycopg

from ports.token_revocation_port import TokenRevocationPort


class PostgresTokenRevocationStore(TokenRevocationPort):
    def __init__(self, db_connection_string: str):
        self.db_url = db_connection_string
        self._ensure_table()

    def _ensure_table(self) -> None:
        if not self.db_url:
            return

        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS revoked_tokens (
                        token_hash VARCHAR(64) PRIMARY KEY,
                        expires_at BIGINT NOT NULL
                    )
                    """
                )
                conn.commit()

    @staticmethod
    def _token_hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def revoke(self, token: str, expires_at: int) -> None:
        if not self.db_url:
            raise ValueError("DB_URL no está configurada.")

        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO revoked_tokens (token_hash, expires_at) VALUES (%s, %s) "
                    "ON CONFLICT (token_hash) DO UPDATE SET expires_at = EXCLUDED.expires_at",
                    (self._token_hash(token), expires_at)
                )
                conn.commit()

    def is_revoked(self, token: str) -> bool:
        if not self.db_url:
            return False

        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM revoked_tokens WHERE expires_at <= EXTRACT(EPOCH FROM NOW())"
                )
                cur.execute(
                    "SELECT 1 FROM revoked_tokens WHERE token_hash = %s",
                    (self._token_hash(token),)
                )
                revoked = cur.fetchone() is not None
                conn.commit()
                return revoked