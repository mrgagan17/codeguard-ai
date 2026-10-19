from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    existing_user = db.query(User).filter(
        or_(
            User.email == payload.email.lower().strip(),
            User.username == payload.username.lower().strip()
        )
    ).first()

    if existing_user:
        if existing_user.email == payload.email.lower().strip():
            raise HTTPException(status_code=400, detail="An account with this email already exists.")
        raise HTTPException(status_code=400, detail="Username is already taken.")

    user = User(
        email=payload.email.lower().strip(),
        username=payload.username.lower().strip(),
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "username": user.username})
    return AuthResponse(access_token=token, user=user)

@router.post("/login", response_model=AuthResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate with username or email and password."""
    ident = payload.username_or_email.lower().strip()
    user = db.query(User).filter(
        or_(
            User.email == ident,
            User.username == ident
        )
    ).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check your username/email and password."
        )

    token = create_access_token({"sub": user.id, "email": user.email, "username": user.username})
    return AuthResponse(access_token=token, user=user)

@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get the currently logged-in user profile."""
    return current_user
