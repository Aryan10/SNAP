import os
import yaml
from dotenv import load_dotenv
from julep import Julep
from functools import lru_cache

# load environment vars from .env
load_dotenv()

# Select model and initialize client
MODEL = os.getenv("JULEP_MODEL", "claude-3.5-sonnet")
client = Julep(
    api_key=os.getenv("JULEP_API_KEY"),
    environment=os.getenv("JULEP_ENVIRONMENT", "production")
)

# Create a classifier agent that flags text as news or not news
classifier_agent = client.agents.create(
    name="News Classifier",
    model=MODEL,
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