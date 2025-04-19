import os
import json
from pathlib import Path
from functools import lru_cache
from tqdm import tqdm
from julep import ConflictError
from .julep_client import client, model

SRC_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = SRC_DIR / "data" / "processed"

agent = client.agents.create(
    name="News RAG Bot",
    model=model,
    about="Answers questions about news articles."
)

def _load_articles(folder_path):
    documents = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if not file.endswith(".json"):
                continue
            with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                data = json.load(f)
            if "content" in data:
                documents.append({
                    "title": data["title"],
                    "content": data["content"],
                    "metadata": {
                        "tags": data.get("tags", []),
                        "location": data.get("location", ""),
                        "category": data.get("category", ""),
                        "publication_date": data.get("publication_date", ""),
                    }
                })
    return documents

def _all_news_document(articles):
    titles = ["News", "All News", "Recent News", "Latest News", "Current News"]
    all_news = []
    for article in articles:
        all_news.append(article["title"])
    doc = {}
    doc["title"] = " | ".join(titles)
    doc["content"] = "\n\n".join(all_news)
    doc["metadata"] = {
        "tags": ["News"],
        "location": "",
        "category": "",
        "publication_date": "",
    }
    return doc

def chatbot_query(query, debug=False):
    results = client.agents.docs.search(
        agent_id=agent.id,
        text=query,
        limit=5
    )

    results_dict = results.model_dump()
    docs = results_dict.get("docs", [])
    
    if not docs:
        return {
            "answer": "No relevant articles found.",
            "sources": []
        }

    if debug:
        print(results.model_dump_json(indent=2))

    # Extract content safely from snippet, with fallback
    context = "\n\n".join([doc.get("snippet", {}).get("content", "") for doc in docs])
    
    return {
        "answer": context,
        "sources": [doc.get("title", "Unknown") for doc in docs]
    }

articles = _load_articles(PROCESSED_DIR)[:5]
articles.append(_all_news_document(articles))
for i in articles:
    print(i["title"])

for doc in tqdm(articles, desc="Uploading articles", unit="doc"):
    try:
        client.agents.docs.create(
            agent_id=agent.id,
            title=doc["title"],
            content=doc["content"],
            metadata=doc["metadata"]
        )
    except ConflictError:
        continue

print(f"Uploaded {len(articles)} articles to agent.")

if __name__ == "__main__":
    while True:
        query = input("\nEnter your news question (or type 'exit'): ").strip()
        if query.lower() in ["exit", "quit"]:
            break

        response = chatbot_query(query)
        print("\nResponse:\n", response["answer"])
        print("\nSources:")
        for title in response["sources"]:
            print("-", title)
