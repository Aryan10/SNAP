import time
from agent.extractor import client, create_task
from cleaner.paragraph_extractor import clean_html
from pathlib import Path
import json
from hashlib import sha256

BASE_DIR = Path(__file__).resolve().parent
prompts_dir = BASE_DIR / "prompt"
articles_dir = BASE_DIR.parent / "data" / "processed"

# Cleaned Input Format: { title, author, publication_date, content }
def extract_news(input, prompt, source=None): 
    task = create_task(prompts_dir / prompt)
    exec_ = client.executions.create(task_id=task.id, input=input)

    print(f"Executing task for: {input['title']}")
    while (res := client.executions.get(exec_.id)).status not in ["succeeded", "failed"]:
        print("Status:", res.status)
        time.sleep(1)

    if res.status == "succeeded":
        string = res.output['choices'][0]['message']['content']
        parsed = json.loads(string)
        parsed["source"] = source
        string = json.dumps(parsed, indent=2)

        # Save Structured Output
        hashed_title = sha256(input['title'].encode('utf-8')).hexdigest()
        with open(articles_dir / f"{hashed_title}.json", "w", encoding="utf-8") as f:
            f.write(string)

        print("Structured Output:\n", string)
        return string
    else:
        print("Execution Failed")
        return None

def extract_news_from_html(html_path, prompt="news_from_html_type1.yaml"):
    input = clean_html(html_path)
    extract_news(input, prompt)

def extract_news_from_reddit():
    file = BASE_DIR / "reddit_test.json"
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    formatted = {}
    post = data[3]
    formatted["title"] = post["title"]
    formatted["author"] = "Unknown"
    formatted["publication_date"] = post["created_utc"]
    formatted["content"] = post["content"]
    extract_news(formatted, prompt="news_from_reddit_post.yaml", source=post)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python run_extraction.py <path_to_html_file>")
    elif sys.argv[1] == "reddit":
        extract_news_from_reddit()
    else:
        extract_news_from_html(sys.argv[1])