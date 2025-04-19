from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent

def reddit_parser(post):
    if post == "debug":
        file = BASE_DIR / "reddit_test.json"
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        post = data[-1]

    if post["content"] == "":
        print("No content found, check if url is news article")
        print(post["url"])
        return None

    formatted = {}

    formatted["title"] = post.get("title", "Unknown")
    formatted["publication_date"] = post.get("created_utc", "Unknown")
    formatted["content"] = post.get("content", post.get("selftext", "No content found, not a news article"))

    return formatted