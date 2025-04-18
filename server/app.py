import os
import jwt
from datetime import datetime, timedelta
from typing import List

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 15

client = AsyncIOMotorClient(DB_URL)
db = client.news_db
users_collection = db.SNAPUsers

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ MODELS ------------------

class RegisterModel(BaseModel):
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class PreferencesModel(BaseModel):
    preferences: List[str]


# ------------------ HELPERS ------------------

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire})
    return jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1] if " " in authorization else authorization
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await users_collection.find_one({"email": email})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ------------------ ROUTES ------------------

@app.post("/register")
async def register(data: RegisterModel):
    existing_user = await users_collection.find_one({"email": data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(data.password)
    user_data = {
        "email": data.email,
        "password": hashed_password,
        "preferences": []
    }
    await users_collection.insert_one(user_data)

    token = create_access_token({"email": data.email})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/login")
async def login(data: LoginModel):
    user = await users_collection.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"email": data.email})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/preferences")
async def update_preferences(data: PreferencesModel, current_user=Depends(get_current_user)):
    await users_collection.update_one(
        {"email": current_user["email"]},
        {"$set": {"preferences": data.preferences}}
    )
    return {"message": "Preferences updated successfully"}

@app.get("/preferences")
async def get_preferences(current_user=Depends(get_current_user)):
    return {"preferences": current_user.get("preferences", [])}

