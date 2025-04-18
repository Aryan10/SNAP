import os
import yaml
from dotenv import load_dotenv
from julep import Julep
from functools import lru_cache

model = os.getenv("JULEP_MODEL", "claude-3.5-sonnet")

load_dotenv()

client = Julep(
    api_key=os.getenv("JULEP_API_KEY"),
    environment=os.getenv("JULEP_ENVIRONMENT", "production")
)

agent = client.agents.create(
    name="News Formatter",
    model=model,
    about="Extracts structured news data from simplified HTML content."
)

@lru_cache(maxsize=None)
def create_task(prompt):
    with open(prompt, "r", encoding="utf-8") as f:
        task_definition = yaml.safe_load(f)

    task = client.tasks.create(agent_id=agent.id, **task_definition)
    return task