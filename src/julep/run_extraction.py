import time
import json
import sys
from pathlib import Path
from hashlib import sha256

from agent.extractor import client, create_task
from agent.formatter import create_formatting_task
from parser.paragraph_extractor import clean_html
from parser.api_parser import reddit_parser
from pathlib import Path
from is_news import is_news

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

            # Format content
            formatted_content = format_news(parsed["content"])
            if formatted_content is None:
                print("Failed to format content")
                return None
            parsed["content"] = formatted_content

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
        return parsed
    else:
        print("Execution Failed")
        return None

def format_news(content, prompt="markdown_formatter.yaml"):
    task = create_formatting_task(prompts_dir / prompt)
    exec_ = client.executions.create(task_id=task.id, input={
        "content": content
    })

    print(f"Executing formatting task for: {content}")
    while (res := client.executions.get(exec_.id)).status not in ["succeeded", "failed"]:
        print("Status:", res.status)
        time.sleep(1)

    if res.status == "succeeded":
        string = res.output['choices'][0]['message']['content']
        print("Formatted Output:\n", string)
        return string
    else:
        print("Execution Failed")
        return None

def extract_news(obj, parser, prompt):
    # Convert input to JSON
    formatted, source = parser(obj)
    if formatted is None:
        return None
    
    news = is_news(formatted)
    if news is None:
        return None

    if not news:
        print("\nNot a news post!")
        return None
    
    article = _extract_news(formatted, prompt=prompt, source=source or obj)
    return article

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_extraction.py <path_to_html_file>")

    elif sys.argv[1] == "reddit":
        file = BASE_DIR / "reddit_test.json"
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        post = data[-1]
        extract_news(post, parser=reddit_parser, prompt="news_from_reddit_post.yaml")

    else:
        extract_news(sys.argv[1], parser=clean_html, prompt="news_from_html_type1.yaml")