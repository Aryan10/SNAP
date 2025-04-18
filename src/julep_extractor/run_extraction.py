import time
from agent_extractor import client, create_task
from cleaner import clean_html
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve()
prompts_dir = BASE_DIR.parent / "prompts"

# Cleaned Input Format: { title, author, publication_date, content }
def extract_news(cleaned_input, prompt): 
    task = create_task(prompts_dir / prompt)
    exec_ = client.executions.create(task_id=task.id, input=cleaned_input)

    print(f"Executing task for: {cleaned_input['title']}")
    while (res := client.executions.get(exec_.id)).status not in ["succeeded", "failed"]:
        print("Status:", res.status)
        time.sleep(1)

    if res.status == "succeeded":
        string = res.output['choices'][0]['message']['content']
        print("Structured Output:\n", string)
        return string
    else:
        print("Execution Failed")
        return None

def extract_news_from_html(html_path, prompt="news_from_html_type1.yaml"):
    cleaned_input = clean_html(html_path)
    extract_news(cleaned_input, prompt)

def extract_news_from_reddit():
    file = "reddit_test.json"
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    formatted = {}
    post = data[3]
    formatted["title"] = post["title"]
    formatted["author"] = "Unknown"
    formatted["publication_date"] = post["created_utc"]
    formatted["content"] = post["content"]
    extract_news(formatted, prompt="news_from_reddit_post.yaml")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python run_extraction.py <path_to_html_file>")
    elif sys.argv[1] == "reddit":
        extract_news_from_reddit()
    else:
        extract_news_from_html(sys.argv[1])