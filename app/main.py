from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import health, auth, employees

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(employees.router)