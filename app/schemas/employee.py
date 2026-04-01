from pydantic import BaseModel, EmailStr
from app.models.employee import UserRole

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.FUNCIONARIO
    department_id: int

class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None
    department_id: int | None = None

class DepartmentOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

class EmployeeOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: str
    role: UserRole
    department: DepartmentOut

    model_config = {"from_attributes": True}