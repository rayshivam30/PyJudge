from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.config.database import get_db
from app.models.entities import Leaderboard, User
from app.schemas.auth import LoginRequest, SignupRequest, TokenPair

router = APIRouter(tags=["Authentication"])


@router.post("/signup", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenPair:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(name=payload.name, email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    db.add(Leaderboard(user_id=user.id))
    db.commit()
    return TokenPair(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.is_banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is banned")
    return TokenPair(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))


@router.post("/refresh", response_model=TokenPair)
def refresh(refresh_token: str) -> TokenPair:
    user_id = decode_token(refresh_token, expected_type="refresh")
    return TokenPair(access_token=create_access_token(user_id), refresh_token=create_refresh_token(user_id))


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Client should discard JWT tokens"}
