from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_manager_or_super
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeOut, EmployeeUpdate
from app.services import employee_service

router = APIRouter(prefix="/employees", tags=["Funcionários"])


@router.post("/", response_model=EmployeeOut, status_code=201)
def create(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_super),
):
    """Cria um novo funcionário. Acesso permitido apenas para 'super' e 'gestor'."""
    return employee_service.create_employee(db, data, current_user)


@router.get("/", response_model=list[EmployeeOut])
def list_all(
    search: str | None = Query(default=None, description="Busca por nome, username ou email"),
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_super),
):
    """Lista todos os funcionários, com opção de busca. Acesso permitido apenas para 'super' e 'gestor'."""
    return employee_service.list_employees(db, current_user, search)


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_one(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_super),
):
    """Obtém os detalhes de um funcionário específico por ID. Acesso permitido apenas para 'super' e 'gestor'."""
    return employee_service.get_employee(db, employee_id, current_user)


@router.patch("/{employee_id}", response_model=EmployeeOut)
def update(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_super),
):
    """Atualiza os dados de um funcionário específico por ID. Acesso permitido apenas para 'super' e 'gestor'."""
    return employee_service.update_employee(db, employee_id, data, current_user)


@router.delete("/{employee_id}", status_code=204)
def delete(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_super),
):
    """Exclui um funcionário específico por ID. Acesso permitido apenas para 'super' e 'gestor'."""
    employee_service.delete_employee(db, employee_id, current_user)