from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.employee import Employee, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Employee:
    """
    Extrai e valida o JWT, depois carrega o Employee do banco.
    Usada como dependência base em rotas protegidas.

    :param str token: O token JWT extraído do header Authorization.
    :param Session db: A sessão do banco de dados.
    :return Employee: O objeto Employee correspondente ao token válido.
    :raises HTTPException: Se o token for inválido, expirado ou se o usuário não for encontrado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    employee = db.query(Employee).filter(Employee.id == user_id).first()
    if employee is None:
        raise credentials_exception

    return employee


def require_super(current_user: Employee = Depends(get_current_user)) -> Employee:
    """
    Permite acesso apenas ao perfil 'super'.
    
    :param Employee current_user: O usuário autenticado, injetado pela dependência get_current_user.
    :return Employee: O mesmo usuário se ele tiver o perfil 'super'.
    :raises HTTPException: Se o usuário não tiver o perfil 'super'.
    """
    if current_user.role != UserRole.SUPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o perfil 'super' pode realizar esta ação.",
        )
    return current_user


def require_manager_or_super(
    current_user: Employee = Depends(get_current_user),
) -> Employee:
    """
    Permite acesso ao 'super' e ao 'gestor'. Bloqueia 'funcionario'.
    
    :param Employee current_user: O usuário autenticado, injetado pela dependência get_current_user.
    :return Employee: O mesmo usuário se ele tiver o perfil 'super' ou 'gestor'.
    :raises HTTPException: Se o usuário tiver o perfil 'funcionario'.
    """
    if current_user.role == UserRole.FUNCIONARIO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a gestores e administradores.",
        )
    return current_user