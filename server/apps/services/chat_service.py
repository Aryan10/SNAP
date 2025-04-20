import sys
import os
import secrets
from typing import Optional
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/julep')))
from run_chatbot import get_chatbot_response
from fastapi import APIRouter
from apps.core.config import DB_URL
from motor.motor_asyncio import AsyncIOMotorClient
router = APIRouter()
client = AsyncIOMotorClient(DB_URL)
articles_collection = client.news_db.articles
users_collection = client.news_db.SNAPUsers

async def get_chat(message: str, article_id:str,current_user: Optional[dict]=None):
    data = await articles_collection.find_one({"id": article_id})
    article = data["content"]
    if(current_user is None):
        random_string = secrets.token_hex(32)  # 32 bytes = 64 hex characters
        return get_chatbot_response(query=message,user_id=random_string,reading=None)
    user_id = await users_collection.find_one({"email": current_user["email"]})
    user_id = user_id["_id"]
    return get_chatbot_response(query=message,user_id=user_id,reading=article)

async def get_chat_without_article(message: str,current_user=None):
    if(current_user is None):
        random_string = secrets.token_hex(32)
        return get_chatbot_response(query=message,user_id=random_string,reading=None)
    user_id = await users_collection.find_one({"email": current_user["email"]})
    user_id = user_id["_id"]
    return get_chatbot_response(query=message,user_id=user_id,reading=None)