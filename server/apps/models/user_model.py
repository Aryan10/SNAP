from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List
from apps.core.config import CATEGORY
class RegisterModel(BaseModel):
    email: EmailStr
    password: str

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class PreferencesModel(BaseModel):
    preferences: List[str]
    category_scores: Dict[str, tuple] = Field(
        default_factory=lambda: {cat: (0, 0.0) for cat in CATEGORY}
    )
    bias: Dict[str, float] = Field(default_factory=lambda: {cat: 1/len(CATEGORY) for cat in CATEGORY})

class UserModel(RegisterModel):
    preferences: PreferencesModel

if __name__ == "__main__":
    prefs = PreferencesModel(preferences=["travel", "economics"])
    user = UserModel(email="user@example.com", password="securepass", preferences=prefs)
    print(user.json(indent=2))
