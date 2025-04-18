# using julep ai for HTML→structured-news conversion with HTML cleaning
import os, time, yaml
from dotenv import load_dotenv
from julep import Julep
from bs4 import BeautifulSoup
from datetime import datetime

# 1. Load environment + initialize Julep client
load_dotenv()
client = Julep(
    api_key=os.getenv("JULEP_API_KEY"),
    environment=os.getenv("JULEP_ENVIRONMENT", "production")
)

# 2. Create agent
agent = client.agents.create(
    name="News Formatter",
    model="claude-3.5-sonnet",  # Recommended for long HTML + reasoning
    about="Extracts structured news data from simplified HTML content."
)

# 3. Create Task (f-string style prompt)
task_definition = yaml.safe_load('''
name: News HTML Formatter
description: |
  Convert cleaned content from a news article into structured JSON.
main:
- prompt:
  - role: system
    content: |
      You are a news article extraction assistant. Extract the following fields:
      - title (string)
      - author (string)
      - publication_date (ISO 8601 string)
      - summary (max 100 words)
      - content (text-only, preserve paragraphs)
      - category (World, Business, Technology, Entertainment, Sports, Science, Health)
      - tags (array of relevant keywords)
  - role: user
    content: |
      Please extract structured information from the following cleaned news content:

      Title: {steps[0].input.title}
      A[0].input.publication_date}
uthor: {steps[0].input.author}
      Published: {steps
      Content:
      {steps[0].input.content}
''')

task = client.tasks.create(agent_id=agent.id, **task_definition)

# 4. Clean HTML using BeautifulSoup
html_path = r"C:\Users\shaur\OneDrive\Desktop\Mycodes\projects\hack36\SNAP\src\scrapped\test2.html"

with open(html_path, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

def get_meta(name):
    tag = soup.find("meta", attrs={"name": name})
    return tag["content"] if tag and tag.get("content") else None

def get_property(prop):
    tag = soup.find("meta", attrs={"property": prop})
    return tag["content"] if tag and tag.get("content") else None

title = get_property("og:title") or (soup.title.string.strip() if soup.title else "Unknown Title")
author = get_meta("author") or "Unknown Author"
date = get_property("article:published_time")
if date:
    try:
        date = datetime.fromisoformat(date).isoformat()
    except ValueError:
        pass
else:
    date = "Unknown"

paragraphs = soup.find_all("p")
content = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

cleaned_input = {
    "title": title,
    "author": author,
    "publication_date": date,
    "content": content[:10000]  # optional truncation
}

# 5. Execute Julep task
exec_ = client.executions.create(task_id=task.id, input=cleaned_input)

# 6. Poll for result
while (res := client.executions.get(exec_.id)).status not in ["succeeded", "failed"]:
    print("Status:", res.status)
    time.sleep(1)

# 7. Print structured JSON result
if res.status == "succeeded":
    string = res.output['choices'][0]['message']['content']
    print(string)
else:
    logs = client.executions.get(exec_.id, logs=True).logs
    print("❌ Execution failed. Logs:\n", logs)
