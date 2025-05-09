import time
import json
import sys
from pathlib import Path
from hashlib import sha256

from agent.extractor import client, create_task
from agent.formatter import create_formatting_task
from agent.classifier import create_classifier_task

from parser.paragraph_extractor import clean_html
from parser.reddit_parser import reddit_parser
from parser.rapid_news_parser import rapid_news_parser
from parser.media_stack_parser import media_stack_parser
from parser.gnews_parser import gnews_parser

BASE_DIR = Path(__file__).resolve().parent
prompts_dir = BASE_DIR / "prompt"
articles_dir = BASE_DIR.parent / "data" / "processed"
test_dir = BASE_DIR / "sample"

def _extract_news(input, prompt, source=None, debug=False): 
    """
    input: { title, publication_date, content }
    prompt: YAML file under prompts_dir
    source: optional
    """
    key = input['title'] + str(input['publication_date'])
    hashed_key = sha256(key.encode('utf-8')).hexdigest()
    article_path = articles_dir / (hashed_key + ".json")

    if article_path.exists():
        print(f"Article already exists: {article_path}")
        return None

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
            parsed["markdown_content"] = _format_news(parsed["content"], debug=debug)
            if parsed["markdown_content"] is None:
                print("Exception: Failed to format content")

            string = json.dumps(parsed, indent=2)
            print("Added markdown content\n")

        except Exception as e:
            print("Error parsing JSON")
            print("Error:", e)
            print("Input:", string)
            return None

        # Save Structured Output
        with open(article_path, "w", encoding="utf-8") as f:
            f.write(string)

        if debug:
            print("Structured Output:\n", string)
        return parsed
    else:
        print("Execution Failed")
        return None


def _is_news(input, prompt="is_news.yaml") -> bool | None:
    task = create_classifier_task(prompts_dir / prompt)
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
        print("Classifier Output (news or not?):\n", result)

        # trim and to lower case
        result = result.strip().lower()
        if result not in ["true", "false"]:
            print("Invalid output")
            return None
        return True if result == "true" else False
    else:
        print("Execution Failed")
        return None

def _format_news(content, prompt="markdown_formatter.yaml", debug=False) -> str | None:
    task = create_formatting_task(prompts_dir / prompt)
    exec_ = client.executions.create(task_id=task.id, input={
        "content": content
    })

    print("Formatting...")
    if debug:
        print(f"Executing formatting task for: {content}")
    while (res := client.executions.get(exec_.id)).status not in ["succeeded", "failed"]:
        print("Status:", res.status)
        time.sleep(1)

    if res.status == "succeeded":
        string = res.output['choices'][0]['message']['content']
        string = string.replace("\n", "\\n")  # <- escape newlines
        if debug:
            print("Formatted Output:\n", string)
        return string
    else:
        print("Execution Failed")
        return None

def extract_news(obj, parser, prompt, assured_news=True, debug=False):
    print("------------------------")
    # Convert input to JSON
    formatted, source = parser(obj)
    if formatted is None:
        return None
    
    # Check if news or not
    if not assured_news:
        is_news = _is_news(formatted)
        if is_news is None:
            return None

        if not is_news:
            print("\nNot a news post!")
            return None
    
    # Generate article
    article = _extract_news(formatted, prompt=prompt, source=source or obj, debug=debug)
    return article

# For debugging only
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_extraction.py <path_to_html_file>")

    elif sys.argv[1] == "reddit":
        file = test_dir / "reddit.json"
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        post = data[-2]
        extract_news(
            post, 
            parser=reddit_parser, 
            prompt="news_from_reddit_post.yaml", 
            assured_news=False,
            debug=True
        )

    elif sys.argv[1] == "rapid_news":
        file = test_dir / "rapid_news.json"
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        news = data[0]
        extract_news(
            news, 
            parser=rapid_news_parser, 
            prompt="news_from_html_type1.yaml",
            debug=True
        )

    elif sys.argv[1] == "media_stack":
        file = test_dir / "media_stack.json"
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        news = data[0]
        extract_news(
            news, 
            parser=media_stack_parser, 
            prompt="news_from_html_type1.yaml",
            debug=True
        )

    elif sys.argv[1] == "gnews":
        file = test_dir / "gnews.json"
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        news = data[0]
        extract_news(
            news, 
            parser=gnews_parser, 
            prompt="news_from_html_type1.yaml",
            debug=True
        )

    else:
        extract_news(
            sys.argv[1], 
            parser=clean_html, 
            prompt="news_from_html_type1.yaml",
            debug=True
        )