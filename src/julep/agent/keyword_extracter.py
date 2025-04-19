import os
import yaml
from functools import lru_cache
from .julep_client import client, model

# Create the QueryKeywordExtractor agent
keyword_agent = client.agents.create(
    name="QueryKeywordExtractor",
    model=model,
    about="Takes a raw user query and distills it into a concise list of keywords or key phrases."
)


@lru_cache(maxsize=None)
def create_task(prompt_file):
    """Create a task from a YAML file."""
    with open(prompt_file, "r", encoding="utf-8") as f:
        task_definition = yaml.safe_load(f)

    task = client.tasks.create(agent_id=keyword_agent.id, **task_definition)
    return task