import time
import json
from pathlib import Path
from agent.is_news import client
from agent.is_news import create_is_news_task as create_task
from cleaner.paragraph_extractor import clean_html
import sys

BASE_DIR = Path(__file__).resolve()
prompts_dir = BASE_DIR.parent / "prompts"

def is_news(cleaned_input, prompt):
    """
    cleaned_input: { title, author, publication_date, content }
    prompt: YAML file under prompts_dir
    """
    task = create_task(prompts_dir / prompt)
    exec_ = client.executions.create(task_id=task.id, input=cleaned_input)

    print(f"Executing is_news task for: {cleaned_input['title']}")
    while True:
        res = client.executions.get(exec_.id)
        if res.status in ("succeeded", "failed"):
            break
        print("Status:", res.status)
        time.sleep(1)

    if res.status == "succeeded":
        result = res.output['choices'][0]['message']['content']
        print("is_news Output:\n", result)
        return result
    else:
        print("Execution Failed")
        return None

def is_news_from_reddit(json_path="reddit_test.json", prompt="is_news.yaml"):
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    post = data[4]
    formatted = {
        "title": post.get("title", ""),
        "author": post.get("author", "Unknown"),
        "publication_date": post.get("created_utc", ""),
        "content": post.get("content", post.get("selftext", ""))
    }
    return is_news(formatted, prompt)

is_news_from_reddit()