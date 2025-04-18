import time
from agent import client, create_task
from cleaner import clean_html
from pathlib import Path

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

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python run_extraction.py <path_to_html_file>")
    else:
        extract_news_from_html(sys.argv[1])