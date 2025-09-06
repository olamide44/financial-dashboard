from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from core.config import settings

class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"

class AuthError(Exception):
    pass

def create_token(sub: str, token_type: str):
    now = datetime.now(timezone.utc)
    if token_type == TokenType.ACCESS:
        exp = now + timedelta(minutes=settings.jwt_access_ttl_min)
    elif token_type == TokenType.REFRESH:
        exp = now + timedelta(days=settings.jwt_refresh_ttl_days)
    else:
        raise ValueError("invalid token type")
    payload = {"sub": sub, "type": token_type, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except JWTError as e:
        raise AuthError("invalid token") from e