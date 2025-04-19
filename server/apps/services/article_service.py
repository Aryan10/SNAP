import json
from pathlib import Path
from fastapi import HTTPException
from apps.models.articles_model import DurationRequest

data_dir = Path(__file__).resolve().parent.parent / "src" / "data" / "processed"

async def get_all_articles(current_user):
    all_articles = []
    for file in sorted(data_dir.glob("*.json")):
        with open(file, "r", encoding="utf-8") as f:
            article = json.load(f)
            article["id"] = file.stem
            all_articles.append(article)
    return {"feeds": all_articles[:20]}

async def get_article_by_id(article_id: str, current_user: dict):
    path = data_dir / f"{article_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Article not found")
    
    with open(path, "r", encoding="utf-8") as f:
        article = json.load(f)
    
    article["popularity"] = article.get("popularity", 0) + 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(article, f, indent=2)

    article["id"] = article_id
    return article

async def update_article_duration(article_id: str, duration: DurationRequest):
    path = data_dir / f"{article_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Article not found")

    with open(path, "r", encoding="utf-8") as f:
        article = json.load(f)

    article["duration"] = article.get("duration", 0) + duration.durationMs / 1000

    with open(path, "w", encoding="utf-8") as f:
        json.dump(article, f, indent=2)

    return {
        "message": "Duration updated",
        "article_id": article_id,
        "added_duration_ms": duration.durationMs,
        "duration": article["duration"]
    }
