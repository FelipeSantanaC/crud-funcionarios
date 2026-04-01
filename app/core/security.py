from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Gera o hash bcrypt de uma senha.
    
    :param str password: A senha em texto plano a ser hashada.
    :return str: O hash da senha.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha bate com o hash.
    
    :param str plain_password: A senha em texto plano.
    :param str hashed_password: O hash da senha.
    :return bool: True se a senha for válida, False caso contrário.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any]) -> str:
    """
    Gera um JWT assinado.

    :param dict data: O payload do token.
    :return str: O token JWT.
    """
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decodifica e valida o JWT.
    
    :param str token: O token JWT a ser decodificado.
    :return dict: O payload do token se for válido.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])