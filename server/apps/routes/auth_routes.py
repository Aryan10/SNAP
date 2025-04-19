from fastapi import APIRouter, HTTPException
from apps.models.user_model import RegisterModel, LoginModel
from apps.services.user_service import register_user, login_user

router = APIRouter()

@router.post("/register")
async def register(data: RegisterModel):
    return await register_user(data)

@router.post("/login")
async def login(data: LoginModel):
    return await login_user(data)
