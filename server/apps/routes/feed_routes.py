from fastapi import APIRouter, HTTPException, Depends
from apps.core.auth import get_optional_user
from apps.services.article_service import get_all_articles, get_article_by_id, update_article_duration
from apps.models.articles_model import DurationRequest
from apps.services.article_service import store_article
router = APIRouter()

@router.get("/feeds")
async def feeds(current_user=Depends(get_optional_user)):
    return await get_all_articles(current_user)

@router.get("/feeds/{article_id}")
async def article(article_id: str, current_user=Depends(get_optional_user)):
    return await get_article_by_id(article_id, current_user)

@router.post("/feeds/{article_id}/track_time")
async def track_time(article_id: str, duration: DurationRequest,current_user=Depends(get_optional_user)):
    print(current_user)
    return await update_article_duration(article_id, duration, current_user)
@router.get("/store_article")
async def store():
    await store_article()
    return {"message": "Article stored successfully"}