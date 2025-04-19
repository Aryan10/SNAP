import os
import yaml
from functools import lru_cache
from .julep_client import client, model

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