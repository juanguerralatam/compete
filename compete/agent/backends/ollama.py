import os
import re
import json
import requests
from typing import List
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ...message import Message

DEFAULT_TEMPERATURE = 0.9
DEFAULT_MAX_TOKENS = 1024
END_OF_MESSAGE = "<EOS>"
STOP = ("<|endoftext|>", END_OF_MESSAGE)
BASE_PROMPT = f"The messages always end with the token {END_OF_MESSAGE}."

OLLAMA_API_URL = "http://localhost:11434/api/chat"

class OllamaChat(IntelligenceBackend):
    stateful = False
    type_name = "ollama-chat"

    def __init__(self, temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS,
                 model: str = "llama3.2", merge_other_agents_as_one_user: bool = False, **kwargs):
        assert is_openai_available, "OpenAI package is not installed or the API key is not set"
        super().__init__(temperature=temperature, max_tokens=max_tokens, model=model,
                         merge_other_agents_as_one_user=merge_other_agents_as_one_user, **kwargs)

        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model
        self.merge_other_agent_as_user = merge_other_agents_as_one_user

    @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=4, max=60))
    def _get_response(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(OLLAMA_API_URL, data=json.dumps(payload), headers=headers)
        print(response.text)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code

        response_data = response.json()
        if 'message' not in response_data or 'content' not in response_data['message']:
            return None  # Or raise an error/handle the missing data as needed

        return response_data['message']['content']

    def query(self, agent_name: str, agent_type: str, role_desc: str, history_messages: List[Message], 
              relationship: str = None, global_prompt: str = None, request_msg: Message = None, *args, **kwargs) -> str:
        messages = []
        
        system_prompt = f"Your name is {agent_name}.\n\nYour role:{role_desc}"
        if global_prompt:
            system_prompt = f"{global_prompt.strip()}\n\n" + system_prompt
        system_prompt += f"\n\n{BASE_PROMPT}"
        
        system_message = {"role": "system", "content": system_prompt}
        messages.append(system_message)
        
        if history_messages:
            user_messages = []
            if len(history_messages) > 12:
                history_messages = history_messages[-12:]
            for msg in history_messages:
                user_messages.append((msg.agent_name, f"{msg.content}{END_OF_MESSAGE}"))

            user_prompt = ""
            for _, msg in enumerate(user_messages):
                user_prompt += f"[{msg[0]}]: {msg[1]}\n"
            user_prompt += f"You are a {agent_type} in a virtual world. Now it's your turn!"
            
            user_message = {"role": "user", "content": user_prompt}
            messages.append(user_message)

        response = self._get_response(messages)
        
        response = re.sub(rf"^\s*\[.*]:", "", response).strip()
        response = re.sub(rf"^\s*{re.escape(agent_name)}\s*:", "", response).strip()
        response = re.sub(rf"{END_OF_MESSAGE}$", "", response).strip()
        
        return response