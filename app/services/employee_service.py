from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from app.models.employee import Employee, UserRole
from app.models.department import Department
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.core.security import hash_password

def _get_employee_or_404(db: Session, employee_id: int) -> Employee:
    """
    Busca um funcionário por ID. Se não encontrado, levanta HTTP 404.

    :param Session db: A sessão do banco de dados.
    :param int employee_id: O ID do funcionário a ser buscado.
    :return Employee: O objeto Employee encontrado.
    :raises HTTPException: Se nenhum funcionário com o ID fornecido for encontrado.
    """
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Funcionário com id {employee_id} não encontrado.",
        )
    return employee

def _check_department_exists(db: Session, department_id: int) -> None:
    """
    Verifica se um departamento com o ID fornecido existe. Se não existir, levanta HTTP 404.

    :param Session db: A sessão do banco de dados.
    :param int department_id: O ID do departamento a ser verificado.
    :raises HTTPException: Se nenhum departamento com o ID fornecido for encontrado.
    """
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Departamento com id {department_id} não encontrado.",
        )

def _assert_same_department(current_user: Employee, target_department_id: int) -> None:
    """
    Garante que gestor só opere dentro do seu departamento.
    
    :param Employee current_user: O usuário autenticado, cujo departamento será comparado.
    :param int target_department_id: O ID do departamento alvo da operação.
    """
    if (
        current_user.role == UserRole.GESTOR
        and current_user.department_id != target_department_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Gestores só podem operar funcionários do seu próprio departamento.",
        )

# ──────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────
def create_employee(
    db: Session, data: EmployeeCreate, current_user: Employee
) -> Employee:
    """
    Cria um novo funcionário, garantindo que as regras de negócio sejam respeitadas:

    - Gestores só podem criar funcionários dentro do seu departamento.
    - Apenas 'super' pode criar gestores ou outros 'super'.
    - Verifica unicidade de username e email.

    :param Session db: A sessão do banco de dados.
    :param EmployeeCreate data: O modelo de dados contendo as informações do novo funcionário.
    :param Employee current_user: O usuário autenticado, usado para verificar permissões.
    :return Employee: O objeto Employee criado.
    :raises HTTPException: Se houver violação de regras de negócio ou conflitos de dados.
    """

    _assert_same_department(current_user, data.department_id)
    _check_department_exists(db, data.department_id)

    conflict = db.query(Employee).filter(
        or_(Employee.username == data.username, Employee.email == data.email)
    ).first()
    if conflict:
        field = "username" if conflict.username == data.username else "email"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um funcionário com este {field}.",
        )

    if data.role in (UserRole.SUPER, UserRole.GESTOR) and current_user.role != UserRole.SUPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o perfil 'super' pode criar gestores ou outros supers.",
        )

    employee = Employee(
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        department_id=data.department_id,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


# ──────────────────────────────────────────
# READ
# ──────────────────────────────────────────
def list_employees(
    db: Session, current_user: Employee, search: str | None = None
) -> list[Employee]:
    """
    Lista funcionários com base no perfil do usuário autenticado:

    - 'super' vê todos os funcionários.
    - 'gestor' vê apenas funcionários do seu departamento.
    Suporta busca por nome, username ou email.

    :param Session db: A sessão do banco de dados.
    :param Employee current_user: O usuário autenticado, usado para filtrar os resultados.
    :param str | None search: Termo de busca para filtrar por nome, username ou email.
    :return list[Employee]: A lista de funcionários que correspondem aos critérios de acesso e busca.
    """
    query = db.query(Employee)

    if current_user.role == UserRole.GESTOR:
        query = query.filter(Employee.department_id == current_user.department_id)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Employee.first_name.ilike(term),
                Employee.last_name.ilike(term),
                Employee.username.ilike(term),
                Employee.email.ilike(term),
            )
        )

    return query.all()

def get_employee(
    db: Session, employee_id: int, current_user: Employee
) -> Employee:
    """
    Obtém os detalhes de um funcionário específico por ID, garantindo que gestores só acessem seu departamento.

    :param Session db: A sessão do banco de dados.
    :param int employee_id: O ID do funcionário a ser obtido.
    :param Employee current_user: O usuário autenticado, usado para verificar permissões.
    :return Employee: O objeto Employee correspondente ao ID fornecido, se o acesso for permitido.
    :raises HTTPException: Se o funcionário não for encontrado ou se o usuário não tiver permissão para acessá-lo.
    """

    employee = _get_employee_or_404(db, employee_id)

    if (
        current_user.role == UserRole.GESTOR
        and employee.department_id != current_user.department_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar este funcionário.",
        )

    return employee

# ──────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────
def update_employee(
    db: Session, employee_id: int, data: EmployeeUpdate, current_user: Employee
) -> Employee:
    """
    Atualiza os dados de um funcionário específico por ID, garantindo que:

    - Gestores só atualizem funcionários do seu departamento.
    - Apenas 'super' pode promover para gestor ou super.
    - Verifica existência do departamento se for alterar.

    :param Session db: A sessão do banco de dados.
    :param int employee_id: O ID do funcionário a ser atualizado.
    :param EmployeeUpdate data: O modelo de dados contendo as informações a serem atualizadas.
    :param Employee current_user: O usuário autenticado, usado para verificar permissões.
    :return Employee: O objeto Employee atualizado.
    :raises HTTPException: Se houver violação de regras de negócio, se o funcionário não for encontrado ou se o usuário não tiver permissão para atualizá-lo.
    """
    employee = _get_employee_or_404(db, employee_id)

    _assert_same_department(current_user, employee.department_id)

    if data.department_id is not None:
        _check_department_exists(db, data.department_id)
        _assert_same_department(current_user, data.department_id)

    if data.role in (UserRole.SUPER, UserRole.GESTOR) and current_user.role != UserRole.SUPER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas o perfil 'super' pode alterar roles para gestor ou super.",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "password" in update_data:
        employee.hashed_password = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(employee, field, value)

    db.commit()
    db.refresh(employee)
    return employee


# ──────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────
def delete_employee(
    db: Session, employee_id: int, current_user: Employee
) -> None:
    """
    Exclui um funcionário específico por ID, garantindo que gestores só excluam dentro do seu departamento e que ninguém possa excluir seu próprio perfil.

    :param Session db: A sessão do banco de dados.
    :param int employee_id: O ID do funcionário a ser excluído.
    :param Employee current_user: O usuário autenticado, usado para verificar permissões.
    :raises HTTPException: Se o funcionário não for encontrado, se o usuário não tiver permissão para excluí-lo ou se o usuário tentar excluir seu próprio perfil.
    """
    employee = _get_employee_or_404(db, employee_id)

    _assert_same_department(current_user, employee.department_id)

    if employee.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não pode deletar seu próprio perfil.",
        )

    db.delete(employee)
    db.commit()