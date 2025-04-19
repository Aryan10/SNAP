from fastapi import HTTPException
from apps.core.security import get_password_hash, verify_password, create_access_token
from apps.models.user_model import RegisterModel, LoginModel
from apps.core.config import DB_URL
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(DB_URL)
users_collection = client.news_db.SNAPUsers

async def register_user(data: RegisterModel):
    if await users_collection.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(data.password)
    await users_collection.insert_one({
        "email": data.email,
        "password": hashed_password,
        "preferences": []
    })

    token = create_access_token({"email": data.email})
    return {"access_token": token, "token_type": "bearer"}

async def login_user(data: LoginModel):
    user = await users_collection.find_one({"email": data.email})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"email": data.email})
    return {"access_token": token, "token_type": "bearer"}

async def update_user_preferences(data, current_user):
    await users_collection.update_one(
        {"email": current_user["email"]},
        {"$set": {"preferences": data.preferences}}
    )
    return {"message": "Preferences updated"}
