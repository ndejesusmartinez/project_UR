import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from ports.token_provider_port import TokenProviderPort

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JwtTokenProvider(TokenProviderPort):
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def generate_token(self, payload: dict) -> str:
        to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=1)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret, algorithms=[self.algorithm])