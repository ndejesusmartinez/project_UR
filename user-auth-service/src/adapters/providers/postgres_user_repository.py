import psycopg
from typing import Optional
from ports.user_repository_port import UserRepositoryPort
from domain.entities.user import User

class PostgresUserRepository(UserRepositoryPort):
    def __init__(self, db_connection_string: str):
        self.db_url = db_connection_string

    def find_by_phone(self, phone: str) -> Optional[User]:
        if not self.db_url:
            return None
            
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, phone, email, role, password_hash, created_at FROM users WHERE phone = %s", 
                    (phone,)
                )
                row = cur.fetchone()
                if not row:
                    return None
                return User(
                    id=str(row[0]), 
                    name=row[1], 
                    phone=row[2], 
                    email=row[3],
                    role=row[4], 
                    password_hash=row[5], 
                    created_at=row[6]
                )

    def find_by_id(self, user_id: str) -> Optional[User]:
        if not self.db_url:
            return None

        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, phone, email, role, password_hash, created_at FROM users WHERE id = %s", 
                    (user_id,)
                )
                row = cur.fetchone()
                if not row:
                    return None
                return User(
                    id=str(row[0]), 
                    name=row[1], 
                    phone=row[2], 
                    email=row[3],
                    role=row[4], 
                    password_hash=row[5], 
                    created_at=row[6]
                )

    def save(self, user: User) -> User:
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (id, name, phone, email, role, password_hash)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING created_at;
                    """,
                    (str(user.id), user.name, user.phone, user.email, user.role, user.password_hash)
                )
                row = cur.fetchone()
                user.created_at = row[0]
                conn.commit()
                return user

    def find_by_email(self, email: str) -> Optional[User]:
        if not self.db_url:
            return None
            
        with psycopg.connect(self.db_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name, phone, email, role, password_hash, created_at FROM users WHERE email = %s", 
                    (email,)
                )
                row = cur.fetchone()
                if not row:
                    return None
                return User(
                    id=str(row[0]), 
                    name=row[1], 
                    phone=row[2], 
                    email=row[3],
                    role=row[4], 
                    password_hash=row[5], 
                    created_at=row[6]
                )