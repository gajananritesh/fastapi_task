from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import Base, engine
from app.routers import auth, employees
from app.middleware import LoggingMiddleware


@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="FastAPI Employee Management CRUD Project", lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

app.include_router(auth.router)
app.include_router(employees.router)

