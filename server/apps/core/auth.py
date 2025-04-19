import jwt
from typing import Optional
from fastapi import Depends, HTTPException,Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from apps.core.config import JWT_SECRET, ALGORITHM,DB_URL
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient(DB_URL)
security = HTTPBearer(auto_error=False)
users_collection = client.news_db.SNAPUsers
def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Returns user payload from JWT if available and valid.
    Otherwise, returns None (for unauthenticated users).
    """
    if not credentials:
        return None

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
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

