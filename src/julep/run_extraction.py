import time
import json
import sys
from pathlib import Path
from hashlib import sha256

from agent.extractor import client, create_task
from cleaner.paragraph_extractor import clean_html
from pathlib import Path
from is_news import is_news
from api_parser import reddit_parser

BASE_DIR = Path(__file__).resolve().parent
prompts_dir = BASE_DIR / "prompt"
articles_dir = BASE_DIR.parent / "data" / "processed"

def _extract_news(input, prompt, source=None): 
    """
    input: { title, publication_date, content }
    prompt: YAML file under prompts_dir
    source: optional
    """
    task = create_task(prompts_dir / prompt)
    exec_ = client.executions.create(task_id=task.id, input=input)

    print(f"Executing task for: {input['title']}")
    while (res := client.executions.get(exec_.id)).status not in ["succeeded", "failed"]:
        print("Status:", res.status)
        time.sleep(1)

    if res.status == "succeeded":
        string = res.output['choices'][0]['message']['content']
        try:
            parsed = json.loads(string)
            parsed["source"] = source
            string = json.dumps(parsed, indent=2)
        except Exception as e:
            print("Error parsing JSON")
            print("Error:", e)
            print("Input:", string)
            return None

        # Save Structured Output
        key = input['title'] + str(input['publication_date'])
        hashed_key = sha256(key.encode('utf-8')).hexdigest()
        with open(articles_dir / f"{hashed_key}.json", "w", encoding="utf-8") as f:
            f.write(string)

        print("Structured Output:\n", string)
        return string
    else:
        print("Execution Failed")
        return None

def extract_news(obj, parser, prompt, source=None):
    formatted = parser(obj)
    news = is_news(formatted)
    if news is not None:
        if news:
            return _extract_news(formatted, prompt=prompt, source=source or obj)
        else:
            print("\nNot a news post!")
            return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_extraction.py <path_to_html_file>")
    elif sys.argv[1] == "reddit":
        extract_news("debug", parser=reddit_parser, prompt="news_from_reddit_post.yaml")
    else:
        extract_news(sys.argv[1], parser=clean_html, prompt="news_from_html_type1.yaml")