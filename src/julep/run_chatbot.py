import time
import json
import sys
from pathlib import Path
from hashlib import sha256
from collections import deque, defaultdict

from agent.chatbot import client, create_chatbot_task
from agent.news_rag_bot import chatbot_query
from agent.keyword_extracter import create_task

BASE_DIR = Path(__file__).resolve().parent
prompts_dir = BASE_DIR / "prompt"

def _filter_prompts(prompt):
    task = create_task(prompts_dir / "filter_prompt.yaml")
    exec_ = client.executions.create(task_id=task.id, input = {'query': prompt})
    print(f"Executing filter task for: {prompt}")
    while (res := client.executions.get(exec_.id)).status not in ["succeeded", "failed"]:
        print("Status:", res.status)
        time.sleep(1)

    if res.status == "succeeded":
        string = res.output['choices'][0]['message']['content']
        print("Filter Output:\n", string)
        return string
    
    else:
        print("Execution Failed")
        return None
    
user_memory = defaultdict(lambda: deque(maxlen=6))

def _get_chatbot_response(query, username="John Doe", prompt="chatbot.yaml"):
    memory = user_memory[username]
    task = create_chatbot_task(prompts_dir / prompt)

    filtered = _filter_prompts(query)
    response = chatbot_query(filtered)
    filtered = response['answer']

    print("Filtered Prompt:\n", filtered)
    if not filtered:
        return None

    exec_ = client.executions.create(
        task_id=task.id, 
        input = {
            'query': query, 
            'content' : filtered,
            'memory': "\n".join(memory)
        }
    )

    print(f"Executing chatbot task for: {query}")
    while (res := client.executions.get(exec_.id)).status not in ["succeeded", "failed"]:
        print("Status:", res.status)
        time.sleep(1)

    if res.status == "succeeded":
        string = res.output['choices'][0]['message']['content']
        print("Chatbot Output:\n", string)

        memory.append(f"User: {query}")
        memory.append(f"Assistant: {string}")

        return string
    else:
        print("Execution Failed")
        return None
    
if __name__ == "__main__":
    while True:
        query = input("\n>> ")
        res = _get_chatbot_response(query)