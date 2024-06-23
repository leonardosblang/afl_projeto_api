import logging
import traceback

from fastapi import FastAPI, Depends, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.endpoints import companies, contracts, auth, dashboard, departments, services
from app.db import session
from app.db.session import engine
from app.dependencies import get_current_user
from app.schemas.user import UserRead, UserCreate

session.Base.metadata.create_all(bind=engine)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logging.error(f"Unhandled error: {traceback.format_exc()}")
            raise e


app = FastAPI()

app.add_middleware(LoggingMiddleware)

app.include_router(auth.router, tags=["auth"])
app.include_router(companies.router, prefix="/companies", tags=["companies"])
app.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(departments.router, prefix="/departments", tags=["departments"])
app.include_router(services.router, prefix="/services", tags=["services"])


@app.on_event("startup")
async def startup_event():
    logging.info("Starting up...")


@app.on_event("shutdown")
async def shutdown_event():
    logging.info("Shutting down...")


@app.get("/")
async def root():
    logging.info("Root endpoint called")
    return {"message": "Hello World"}


@app.post("/register")
async def register_user(user: UserCreate):
    logging.info("Register endpoint called")
    return {"message": "User registered"}


@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user: UserRead = Depends(get_current_user)):
    return current_user
