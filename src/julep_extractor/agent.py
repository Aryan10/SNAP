import os
import yaml
from dotenv import load_dotenv
from julep import Julep
from pathlib import Path

BASE_DIR = Path(__file__).resolve()
prompts_dir = BASE_DIR.parent / "prompts"

news_prompt = prompts_dir / "news_prompt.yaml"

load_dotenv()

client = Julep(
    api_key=os.getenv("JULEP_API_KEY"),
    environment=os.getenv("JULEP_ENVIRONMENT", "production")
)

agent = client.agents.create(
    name="News Formatter",
    model="claude-3.5-sonnet",
    about="Extracts structured news data from simplified HTML content."
)

with open(news_prompt, "r", encoding="utf-8") as f:
    task_definition = yaml.safe_load(f)

task = client.tasks.create(agent_id=agent.id, **task_definition)
