from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import hashlib
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/mysafety"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"charset": "utf8mb4"})

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/register")
async def register_user(user: UserCreate):
    hashed_password = hash_password(user.password)
    with engine.connect() as conn:
        # Check if email exists
        result = conn.execute(
            text("SELECT user_id FROM appuser WHERE email = :email"),
            {"email": user.email}
        ).fetchone()
        if result:
            raise HTTPException(status_code=400, detail="Email already registered")
        # Insert new user
        conn.execute(
            text("""
                INSERT INTO appuser (email, username, password_hash, role_hint, status, created_at)
                VALUES (:email, :username, :password_hash, :role_hint, :status, :created_at)
            """),
            {
                "email": user.email,
                "username": user.username,
                "password_hash": hashed_password,
                "role_hint": "User",
                "status": "Active",
                "created_at": datetime.utcnow()
            }
        )
    return {"message": "User registered successfully"}

@app.post("/login")
async def login_user(user: UserLogin):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM appuser WHERE email = :email"),
            {"email": user.email}
        ).mappings().fetchone()
        if not result:
            raise HTTPException(status_code=400, detail="Email not registered")
        stored_password = result["password_hash"]
        if stored_password != hash_password(user.password):
            raise HTTPException(status_code=400, detail="Incorrect password")
        return {
            "message": "Login successful",
            "user": {
                "email": result["email"],
                "username": result["username"],
                "role_hint": result["role_hint"],
                "station_id": result["station_id"],
                "status": result["status"],
                "created_at": result["created_at"]
            }
        }

@app.get("/")
def read_root():
    return {"message": "Welcome to Safe Route App API"}