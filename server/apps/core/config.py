import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 15
