from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
from datetime import datetime

# FastAPI app
app = FastAPI()

# Database connection setup
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://username:password@localhost/mysafety"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"charset": "utf8mb4"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# User table model
class User(Base):
    __tablename__ = 'APPUSER'

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(150), unique=True, index=True)
    password = Column(String(255))
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables (run only once)
Base.metadata.create_all(bind=engine)

# Pydantic models for registration and login
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str = None

class UserLogin(BaseModel):
    email: str
    password: str

# Utility functions for password hashing
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register a new user
@app.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create a new user
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password, full_name=user.full_name)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

# User login
@app.post("/login")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # Check if the email exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not registered")
    
    # Verify password
    if not verify_password(db_user.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {"message": "Login successful", "user": db_user.email}

