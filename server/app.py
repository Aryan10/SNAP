import os
import jwt
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List,Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv
from apps.models.user import RegisterModel, LoginModel, PreferencesModel
load_dotenv()

DB_URL = os.getenv("DB_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 15

security = HTTPBearer(auto_error=False)
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



# ------------------ HELPERS ------------------
async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if credentials:
        token = credentials.credentials
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload  # Or fetch user from DB if needed
        except Exception:
            return None
    return None

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

@app.get("/feeds")
async def get_feeds(current_user: Optional[dict] = Depends(get_optional_user)):
    data_dir = Path(__file__).resolve().parent.parent / "src" / "data" / "processed"
    all_articles = []

    # Read all .json files
    for file in sorted(data_dir.glob("*.json")):
        with open(file, "r", encoding="utf-8") as f:
            article = json.load(f)
            article["id"] = file.stem
            all_articles.append(article)

    # If user is logged in, you can personalize here (future extension)
    if current_user:
        # Optional: Use current_user["preferences"] to re-sort/filter
        pass

    # Top 20 articles
    top_articles = all_articles[:20]

    return {"feeds": top_articles}
@app.get("/feeds/{article_id}")
async def get_article(article_id: str, current_user: Optional[dict] = Depends(get_optional_user)):
    data_dir = Path(__file__).resolve().parent.parent / "src" / "data" / "processed"
    article_path = data_dir / f"{article_id}.json"

    if not article_path.exists():
        raise HTTPException(status_code=404, detail="Article not found")

    with open(article_path, "r", encoding="utf-8") as f:
        article = json.load(f)

    tags = article.get("tags", [])

    # Update user category_scores in MongoDB
    if current_user:
        user_id = current_user.get("_id") or current_user.get("id")  # Adjust depending on your schema
        if user_id:
            updates = {}
            for tag in tags:
                updates[f"category_scores.{tag}"] = 1

            # Use $inc to increment each tag
            await users_collection.update_one(
                {"_id": user_id},
                {"$inc": updates}
            )

    # Update article popularity
    article["popularity"] = article.get("popularity", 0) + 1

    with open(article_path, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)

    article["id"] = article_id
    return article
@app.post("/feeds/{article_id}/track_time")
async def track_time(article_id: str, durationMs: float):
    data_dir = Path(__file__).resolve().parent.parent / "src" / "data" / "processed"
    article_path = data_dir / f"{article_id}.json"

    if not article_path.exists():
        raise HTTPException(status_code=404, detail="Article not found")

    # Load the article JSON
    with open(article_path, "r", encoding="utf-8") as f:
        article = json.load(f)

    # Update duration
    previous_duration = article.get("duration", 0)
    article["duration"] = previous_duration + durationMs

    # Save back the updated article
    with open(article_path, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)

    return {
        "message": "Duration updated",
        "article_id": article_id,
        "added_duration_ms": durationMs,
        "duration": article["duration"]
    }