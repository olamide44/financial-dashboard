from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from core.deps import get_db, get_current_user
from core.security import create_token, TokenType
from db import models

router = APIRouter()
ph = PasswordHasher()

@router.post("/signup", status_code=201)
def signup(email: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already in use")
    user = models.User(email=email, pass_hash=ph.hash(password))
    db.add(user)
    account = models.Account(user=user, display_name="Default")
    db.add(account)
    db.commit()
    access = create_token(str(user.id), TokenType.ACCESS)
    refresh = create_token(str(user.id), TokenType.REFRESH)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    try:
        ph.verify(user.pass_hash, form.password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_token(str(user.id), TokenType.ACCESS)
    refresh = create_token(str(user.id), TokenType.REFRESH)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

@router.get("/me")
def me(current_user: models.User = Depends(get_current_user)):
    return {"id": str(current_user.id), "email": current_user.email, "role": current_user.role, "created_at": current_user.created_at}