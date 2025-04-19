import os
import yaml
from functools import lru_cache
from .julep_client import client, model

# Create a classifier agent that flags text as news or not news
classifier_agent = client.agents.create(
    name="News Classifier",
    model=model,
    about="Classifies input text as news or not news."
)

@lru_cache(maxsize=None)
def create_classifier_task(yaml_path: str = "is_news.yaml"):
    """
    Reads a YAML task definition for 'is_news' and registers it under the classifier agent.
    Returns the created task object.
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        task_definition = yaml.safe_load(f)

    task = client.tasks.create(agent_id=classifier_agent.id, **task_definition)
    return task