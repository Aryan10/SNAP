import os
import yaml
from functools import lru_cache
from .julep_client import client, model

# Create a chatbot agent that interacts with users and provides information
chatbot_agent = client.agents.create(
    name="Chatbot",
    model=model,
    about="A chatbot that interacts with users and provides information."
)

@lru_cache(maxsize=None)
def create_chatbot_task(yaml_path: str = "chatbot.yaml"):
    """
    Reads a YAML task definition for 'chatbot' and registers it under the chatbot agent.
    Returns the created task object.
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        task_definition = yaml.safe_load(f)

    task = client.tasks.create(agent_id=chatbot_agent.id, **task_definition)
    return task