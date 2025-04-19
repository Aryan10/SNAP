import json
from pathlib import Path
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from apps.models.articles_model import DurationRequest
from dotenv import load_dotenv
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

load_dotenv()

DB_URL = os.getenv("DB_URL")
client = AsyncIOMotorClient(DB_URL)
db = client.news_db
articles_collection = db.articles

data_dir = Path(__file__).resolve().parent.parent.parent.parent / "src" / "data" / "processed"

# -------------------- MIGRATION HELPER --------------------
async def store_article():
    for file in sorted(data_dir.glob("*.json")):
        with open(file, "r", encoding="utf-8") as f:
            article = json.load(f)
            article["id"] = file.stem

            # Upsert article into MongoDB
            existing = await articles_collection.find_one({"id": article["id"]})
            if not existing:
                await articles_collection.insert_one(article)


# -------------------- MAIN SERVICES -----------------------
async def get_all_articles(current_user):
    articles_cursor = articles_collection.find().sort("popularity", -1).limit(20)
    articles_raw = await articles_cursor.to_list(length=20)
    
    articles = []
    for doc in articles_raw:
        doc["_id"] = str(doc["_id"])  # convert ObjectId to string
        articles.append(doc)

    return {"feeds": articles}

# Keep this function as is
async def store_article():
    for file in sorted(data_dir.glob("*.json")):
        with open(file, "r", encoding="utf-8") as f:
            article = json.load(f)
            article["id"] = file.stem
            existing = await articles_collection.find_one({"id": article["id"]})
            if not existing:
                await articles_collection.insert_one(article)

scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.add_job(store_article, IntervalTrigger(hours=24))
    scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()


async def get_article_by_id(article_id: str, current_user: dict):
    article = await articles_collection.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Increment popularity
    await articles_collection.update_one({"id": article_id}, {"$inc": {"popularity": 1}})

    # Reload updated article
    article["popularity"] = 1+article.get("popularity", 0)
    article["_id"] = str(article["_id"])  # convert ObjectId to string
    return article

async def update_article_duration(article_id: str, duration: DurationRequest):
    article = await articles_collection.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    added_seconds = duration.durationMs / 1000
    new_duration = article.get("duration", 0) + added_seconds

    await articles_collection.update_one(
        {"id": article_id},
        {"$set": {"duration": new_duration}}
    )

    return {
        "message": "Duration updated",
        "article_id": article_id,
        "added_duration_ms": duration.durationMs,
        "duration": new_duration
    }

# if __name__ == "__main__":
#     store_article()
