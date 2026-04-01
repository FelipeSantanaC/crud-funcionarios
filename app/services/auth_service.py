from sqlalchemy.orm import Session

from app.core.security import verify_password, create_access_token
from app.models.employee import Employee

def authenticate_employee(db: Session, username: str, password: str) -> Employee | None:
    """
    Busca o employee pelo username e verifica a senha.
    Retorna o Employee se válido, None caso contrário.

    :param Session db: A sessão do banco de dados.
    :param str username: O nome de usuário do funcionário.
    :param str password: A senha em texto plano a ser verificada.
    :return Employee | None: O objeto Employee se as credenciais forem válidas, ou None caso contrário.
    """
    employee = db.query(Employee).filter(Employee.username == username).first()
    if not employee:
        return None
    if not verify_password(password, employee.hashed_password):
        return None
    return employee


def build_token_for(employee: Employee) -> str:
    """
    Monta o payload com as informações relevantes para autorização e gera o JWT.

    :param Employee employee: O objeto Employee para o qual o token será gerado.
    :return str: O token JWT gerado para o funcionário.
    """
    payload = {
        "sub": employee.username,
        "user_id": employee.id,
        "role": employee.role.value,
        "department_id": employee.department_id,
    }
    return create_access_token(payload)