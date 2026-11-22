from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.models import Token, User, UserCreate, UserPublic
from app.security import (
    CurrentUser,
    SessionDep,
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, session: SessionDep):
    # Check if username or email already exists
    existing_user = session.exec(
        select(User).where((User.username == user_in.username) | (User.email == user_in.email))
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/token", response_model=Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(username=user.username)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserPublic)
def get_me(current_user: CurrentUser):
    return current_user
