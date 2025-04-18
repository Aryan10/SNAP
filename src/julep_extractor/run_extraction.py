import time
from agent import client, task
from cleaner import clean_html

def extract_news(html_path):
    cleaned_input = clean_html(html_path)
    exec_ = client.executions.create(task_id=task.id, input=cleaned_input)

    print(f"Executing task for: {html_path}")
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python run_extraction.py <path_to_html_file>")
    else:
        extract_news(sys.argv[1])
