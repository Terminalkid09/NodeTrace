from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.ratelimit import limiter

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register_admin(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="user_exists")

    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password)
    )

    db.add(user)
    db.commit()

    return {"status": "admin_created"}

@router.post("/login")
@limiter.limit("5/minute")
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid_credentials")

    token = create_access_token({"sub": user.username})
    return {"status": "ok", "access_token": token}
