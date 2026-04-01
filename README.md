# 👥 Employee Profile Manager

> API REST para gerenciamento de perfis de funcionários internos, com autenticação JWT e controle de acesso por perfil.

---

## 📌 Sobre o Projeto

O **Employee Profile Manager** é uma API desenvolvida com **FastAPI** e **PostgreSQL** que permite gerenciar perfis de funcionários de uma empresa de forma segura e organizada. O sistema conta com três níveis de acesso (`super`, `gestor`, `funcionario`), garantindo que cada usuário enxergue e opere apenas o que lhe é permitido.

---

## 🚀 Tecnologias

| Tecnologia | Uso |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Framework web assíncrono |
| [PostgreSQL](https://www.postgresql.org/) | Banco de dados relacional |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM |
| [Pydantic](https://docs.pydantic.dev/) | Validação de dados |
| [python-jose](https://github.com/mpdavis/python-jose) | Geração e validação de JWT |
| [passlib + bcrypt](https://passlib.readthedocs.io/) | Hash de senhas |
| [Docker + Docker Compose](https://www.docker.com/) | Containerização do banco |

---

## 📁 Estrutura do Projeto

```
app/
├── core/
│   ├── config.py          # Configurações e variáveis de ambiente (Pydantic Settings)
│   ├── database.py        # Engine e sessão do SQLAlchemy
│   └── security.py        # Hash de senha, geração e decodificação de JWT
│
├── models/
│   ├── department.py      # Model de Departamento
│   └── employee.py        # Model de Funcionário + Enum de roles
│
├── schemas/
│   ├── auth.py            # Schemas de login e token
│   └── employee.py        # Schemas de criação, atualização e resposta
│
├── services/
│   ├── auth_service.py    # Lógica de autenticação
│   └── employee_service.py # Regras de negócio do CRUD
│
├── dependencies/
│   └── auth.py            # Dependências reutilizáveis (get_current_user, require_super...)
│
├── routers/
│   ├── auth.py # Endpoints de autenticação
│   ├── employees.py # Endpoints de funcionários
│   └── health.py # Endpoint de saúde da API
│
└── main.py                # Entrypoint da aplicação
```

---

## ⚙️ Configuração e Execução

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose

### 1. Clone o repositório

```bash
git clone https://github.com/FelipeSantanaC/crud-funcionarios
cd crud-funcionarios
```

### 2. Crie o ambiente virtual e instale as dependências

```bash
uv sync # Já cria o ambiente virtual e instala as dependencias por causa do pyproject.toml

# Ou você pode criar normalmente e instalar à partir dos requirements.txt

python -m venv .venv
source .venv/bin/activate  # Linux
.venv\Scripts\activate # Windows

pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/employees_db
SECRET_KEY=sua_chave_secreta_aqui  # Gere sua chave secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Suba o banco de dados com Docker

```bash
docker compose up -d
```

### 5. Inicie a aplicação

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.  
Documentação interativa: `http://localhost:8000/docs`

---

## 🔐 Autenticação

A API utiliza **JWT (JSON Web Token)**. Para acessar as rotas protegidas:

**1. Faça login:**

```http
POST /auth/login
Content-Type: application/json

{
  "username": "seu_usuario",
  "password": "sua_senha"
}
```

**2. Use o token retornado no header das requisições:**

```http
Authorization: Bearer <access_token>
```

---

## 📋 Endpoints

### 🔑 Autenticação

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/auth/login` | Login via JSON (Postman/Insomnia) |

### 👤 Funcionários

| Método | Rota | Descrição | Acesso |
|---|---|---|---|
| `POST` | `/employees/` | Criar funcionário | `super`, `gestor` |
| `GET` | `/employees/` | Listar funcionários | `super`, `gestor` |
| `GET` | `/employees/?search=ana` | Buscar por nome/username/email | `super`, `gestor` |
| `GET` | `/employees/{id}` | Buscar funcionário por ID | `super`, `gestor` |
| `PATCH` | `/employees/{id}` | Atualizar funcionário | `super`, `gestor` |
| `DELETE` | `/employees/{id}` | Deletar funcionário | `super`, `gestor` |

---

## 🛡️ Controle de Acesso por Perfil

| Ação | `super` | `gestor` | `funcionario` |
|---|---|---|---|
| Listar funcionários | ✅ Todos | ✅ Só seu depto | ❌ |
| Buscar por ID | ✅ Qualquer | ✅ Só seu depto | ❌ |
| Criar funcionário | ✅ Qualquer depto | ✅ Só seu depto | ❌ |
| Criar gestor / super | ✅ | ❌ | ❌ |
| Atualizar funcionário | ✅ Qualquer | ✅ Só seu depto | ❌ |
| Deletar funcionário | ✅ Qualquer | ✅ Só seu depto | ❌ |

> Nenhum usuário pode deletar o próprio perfil.

---

## 📦 Payload do JWT

O token carrega as informações necessárias para autorização em cada requisição:

```json
{
  "sub": "username",
  "user_id": 1,
  "role": "gestor",
  "department_id": 2,
  "exp": 1712000000
}
```

---

## 💡 Exemplos de Uso

### Criar um funcionário

```http
POST /employees/
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Ana",
  "last_name": "Silva",
  "username": "ana.silva",
  "email": "ana@empresa.com",
  "password": "senha123",
  "role": "funcionario",
  "department_id": 1
}
```

### Buscar funcionários com filtro

```http
GET /employees/?search=ana
Authorization: Bearer <token>
```

### Atualizar parcialmente um perfil

```http
PATCH /employees/5
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "novo.email@empresa.com"
}
```

---

## 🗂️ Roles disponíveis

| Role | Descrição |
|---|---|
| `super` | Administrador com acesso total ao sistema |
| `gestor` | Gerencia funcionários do seu próprio departamento |
| `funcionario` | Sem acesso às rotas de gerenciamento |

---
