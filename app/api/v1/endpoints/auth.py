import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.crud import crud_user
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserRead

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud_user.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    logging.debug(f"Registering user with email: {user.email}")
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        logging.warning("Email already registered")
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_user.create_user(db=db, user=user)
