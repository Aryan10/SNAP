import json
from pathlib import Path
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apps.models.articles_model import DurationRequest
from apps.core.config import DB_URL
from apps.utils.recommendation import sort_articles, update_weights
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize scheduler for daily migrations
scheduler = AsyncIOScheduler()
client = AsyncIOMotorClient(DB_URL)
articles_collection = client.news_db.articles
users_collection = client.news_db.SNAPUsers
# Directory containing JSON articles
data_dir = Path(__file__).resolve().parent.parent.parent.parent / "src" / "data" / "processed"

async def store_article():
    """Load articles from JSON files into MongoDB if not present."""
    for file in sorted(data_dir.glob("*.json")):
        with open(file, "r", encoding="utf-8") as f:
            article = json.load(f)
            article["id"] = file.stem

            existing = await articles_collection.find_one({"id": article["id"]})
            if not existing:
                await articles_collection.insert_one(article)


def start_scheduler():
    scheduler.add_job(store_article, IntervalTrigger(hours=24))
    scheduler.start()


def shutdown_scheduler():
    scheduler.shutdown()

async def get_all_articles(current_user: dict):
    """
    Return top 20 articles, personalized if user is logged in.
    Uses user's category_scores as weights for recommendation.
    """
    # Fetch raw articles
    cursor = articles_collection.find().limit(50)
    raw_articles = await cursor.to_list(length=50)

    # Convert ObjectId->_id to string
    for doc in raw_articles:
        doc["_id"] = str(doc.get("_id"))

    # If no user or no category_scores, fallback to popularity sort
    if not current_user or not current_user.get("category_scores"):
        sorted_by_pop = sorted(raw_articles, key=lambda a: a.get("popularity", 0), reverse=True)
        return {"feeds": sorted_by_pop[:20]}

    # Extract user data
    preferences = current_user.get("preferences", [])
    raw_weights = current_user.get("bias", {})
    # Load interaction data, default empty
    interactions = current_user.get("category_scores", {cat: (0, 0.0) for cat in preferences})

    # Generate personalized ordering
    personalized = sort_articles(preferences, raw_weights, interactions, raw_articles)
    top20 = personalized[:20]

    return {"feeds": top20}

async def get_article_by_id(article_id: str, current_user: dict):
    article = await articles_collection.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Increment popularity in DB
    await articles_collection.update_one({"id": article_id}, {"$inc": {"popularity": 1}})
    # Reflect increment locally
    article["popularity"] = article.get("popularity", 0) + 1
    article["_id"] = str(article.get("_id"))
    return article

async def update_article_duration(article_id: str, duration: DurationRequest, current_user: dict ):
    article = await articles_collection.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    added_seconds = duration.durationMs / 1000
    new_duration = article.get("duration", 0) + added_seconds
    # Update in DB
    await articles_collection.update_one(
        {"id": article_id},
        {"$set": {"duration": new_duration}}
    )
    print(current_user)
    # Optionally update user's interaction and weights
    if current_user:
        user_id = current_user.get("email")
        cat = article.get("category")
        # Fetch latest user doc
        user_doc = await users_collection.find_one({"email": user_id})
        prefs = user_doc.get("preferences", [])
        raw_weights = user_doc.get("bias", {})
        # Normalize existing weights
        total_w = sum(raw_weights.values()) or 1.0
        weights = {c: raw_weights.get(c, 0) / total_w for c in prefs}
        inter = user_doc.get("category_scores", {c: (0,0.0) for c in prefs})
        # Update weights based on view
        new_weights = update_weights(weights, inter, cat, clicked=True, duration=added_seconds)
        # Save back
        # Denormalize weights back to category_scores scale
        updated_scores = {c: new_weights.get(c, 0) for c in prefs}
        print("Updated Scores", updated_scores)
        await users_collection.update_one(
            {"email": user_id},
            {"$set": {"bias": new_weights, "category_scores": inter}}
        )

    return {
        "message": "Duration updated",
        "article_id": article_id,
        "added_duration_ms": duration.durationMs,
        "duration": new_duration
    }

# For testing
if __name__ == '__main__':
    import asyncio
    asyncio.run(store_article())
