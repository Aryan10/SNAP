import time
import json
from pathlib import Path
from agent.is_news import client
from agent.is_news import create_is_news_task as create_task
from parser.paragraph_extractor import clean_html
import sys

BASE_DIR = Path(__file__).resolve().parent
prompts_dir = BASE_DIR / "prompt"

def is_news(input, prompt="is_news.yaml") -> bool | None:
    """
    input: { title, author, publication_date, content }
    prompt: YAML file under prompts_dir
    """
    task = create_task(prompts_dir / prompt)
    exec_ = client.executions.create(task_id=task.id, input=input)

    print(f"Executing is_news task for: {input['title']}")
    while True:
        res = client.executions.get(exec_.id)
        if res.status in ("succeeded", "failed"):
            break
        print("Status:", res.status)
        time.sleep(1)

    if res.status == "succeeded":
        result = res.output['choices'][0]['message']['content']
        print("is_news Output:\n", result)

        # trim and to lower case
        result = result.strip().lower()
        if result not in ["true", "false"]:
            print("Invalid output")
            return None
        return True if result == "true" else False
    else:
        print("Execution Failed")
        return None

# for debugging only
def is_news_from_reddit(json_path=BASE_DIR / "reddit_test.json", prompt="is_news.yaml"):
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

if __name__ == "__main__":
    is_news_from_reddit()