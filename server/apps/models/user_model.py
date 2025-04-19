from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List

default_categories = [
    "accident", "travel", "economics", "entertainment", "sports",
    "technology", "health", "science", "politics", "business",
    "education", "crime", "environment", "agriculture", "weather",
    "disaster", "culture", "religion", "finance", "real_estate",
    "automobile", "startups", "market", "energy", "military",
    "diplomacy", "immigration", "law", "human_rights", "media",
    "fashion", "food", "lifestyle", "parenting", "psychology",
    "space", "astronomy", "social_media", "gadgets", "AI",
    "cybersecurity", "blockchain", "cryptocurrency", "celebrity",
    "movies", "music", "television", "books", "art", "history",
    "philosophy", "biology", "chemistry", "physics", "mathematics",
    "mental_health", "pandemic", "vaccine", "public_safety",
    "transportation", "infrastructure", "labor", "gender", "race",
    "election", "international", "local", "opinion", "editorial",
    "breaking_news", "trending", "weird", "innovation"
]

class RegisterModel(BaseModel):
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class PreferencesModel(BaseModel):
    preferences: List[str]
    category_scores: Dict[str, int] = Field(
        default_factory=lambda: {cat: 0 for cat in default_categories}
    )

class UserModel(RegisterModel):
    preferences: PreferencesModel

if __name__ == "__main__":
    prefs = PreferencesModel(preferences=["travel", "economics"])
    user = UserModel(email="user@example.com", password="securepass", preferences=prefs)
    print(user.json(indent=2))
