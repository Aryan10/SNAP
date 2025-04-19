import os
from dotenv import load_dotenv
from julep import Julep

# load environment vars from .env
load_dotenv()

# Select model and initialize client
model = os.getenv("JULEP_MODEL", "claude-3.5-sonnet")

client = Julep(
    api_key=os.getenv("JULEP_API_KEY"),
    environment=os.getenv("JULEP_ENVIRONMENT", "production")
)