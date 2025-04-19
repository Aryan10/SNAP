import os
import yaml
from functools import lru_cache
from .julep_client import client, model

# Create a separate agent for formatting
formatter_agent = client.agents.create(
    name="Markdown Formatter",
    model=model,
    about="Applies Markdown formatting to the content field of news JSON."
)

@lru_cache(maxsize=None)
def create_formatting_task(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        task_definition = yaml.safe_load(f)

    task = client.tasks.create(agent_id=formatter_agent.id, **task_definition)
    return task
