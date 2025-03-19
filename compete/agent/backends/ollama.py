import os
import re
import json
import logging
import requests
from typing import List, Dict
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ...message import Message

DEFAULT_TEMPERATURE = 0.9
DEFAULT_MAX_TOKENS = 1024
END_OF_MESSAGE = "<EOS>"
STOP = ("", END_OF_MESSAGE)
BASE_PROMPT = f"Messages end with {END_OF_MESSAGE}. Respond ONLY with valid JSON using the specified format."
OLLAMA_API_URL = "http://localhost:11434/api/chat"

JSON_TEMPLATE = """{
    "type": "<action_type>",
    "data": {
        // Your content here
    }
}"""

class OllamaChat(IntelligenceBackend):
    stateful = False
    type_name = "ollama-chat"

    def __init__(self, temperature: float = DEFAULT_TEMPERATURE, max_tokens: int = DEFAULT_MAX_TOKENS,
                 model: str = "qwen2.5:72b", merge_other_agents_as_one_user: bool = False, **kwargs):
        super().__init__(temperature=temperature, max_tokens=max_tokens, model=model,
                         merge_other_agents_as_one_user=merge_other_agents_as_one_user, **kwargs)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model
        self.merge_other_agent_as_user = merge_other_agents_as_one_user

    @retry(stop=stop_after_attempt(6), wait=wait_random_exponential(min=4, max=60))
    def _get_response(self, messages: List[Dict]) -> str:
        """Handle API communication with enhanced error handling and validation."""
        try:
            response = requests.post(
                OLLAMA_API_URL,
                json={"model": self.model, "messages": messages, "stream": False},
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            response.raise_for_status()
            
            response_data = response.json()
            if not isinstance(response_data, dict):
                raise ValueError("Invalid API response format")
            
            if 'message' not in response_data or 'content' not in response_data['message']:
                raise ValueError("Invalid response structure")
            
            return str(response_data['message']['content']).strip()
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {response.text[:200]}") from e
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"API connection failed: {str(e)}") from e

    def _build_system_prompt(self, agent_name: str, role_desc: str, global_prompt: str = None) -> str:
        """Construct the system prompt with validation and efficient string handling."""
        components = []
        if global_prompt:
            components.append(global_prompt.strip())
        components.append(f"You are {agent_name}.\n\nRole Description: {role_desc}")
        components.append(BASE_PROMPT)
        components.append(f"Use this JSON template:\n{JSON_TEMPLATE}")
        return '\n\n'.join(components)

    def _process_history(self, history_messages: List[Message], agent_type: str) -> str:
        """Process historical messages into a formatted prompt with efficient truncation."""
        if not history_messages:
            return ""
            
        processed = []
        for msg in history_messages[-12:]:  # Keep last 12 messages
            if hasattr(msg, 'agent_name') and hasattr(msg, 'content'):
                content = str(msg.content or "") + END_OF_MESSAGE
                processed.append(f"[{msg.agent_name}]: {content}")
        
        return '\n'.join(processed) + f"\n\nAs a {agent_type}, respond with valid JSON:"

    def _validate_json_response(self, response: str) -> str:
        """Validate and normalize JSON response with comprehensive checks."""
        try:
            # Extract JSON from potential surrounding text
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object detected in response")
            
            parsed = json.loads(json_match.group())
            if not isinstance(parsed, dict):
                parsed = {"type": "text", "data": parsed}
                
            if 'type' not in parsed:
                parsed['type'] = "text"
            if 'data' not in parsed:
                parsed['data'] = {}
                
            return json.dumps(parsed, ensure_ascii=False)
            
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing failed: {str(e)}")
            raise ValueError("Invalid JSON format") from e
        except Exception as e:
            logging.error(f"JSON validation error: {str(e)}")
            raise ValueError("Invalid response structure") from e

    def query(self, agent_name: str, agent_type: str, role_desc: str, 
              history_messages: List[Message], global_prompt: str = None, 
              request_msg: Message = None, **kwargs) -> str:
        """Optimized query handler with streamlined JSON processing."""
        try:
            # Validate core parameters
            if not isinstance(agent_name, str) or not agent_name.strip():
                raise ValueError("Invalid agent name")
            if not isinstance(role_desc, str) or not role_desc.strip():
                raise ValueError("Invalid role description")

            # Build message chain
            messages = [{
                "role": "system",
                "content": self._build_system_prompt(agent_name, role_desc, global_prompt)
            }]

            # Add historical context
            if history_prompt := self._process_history(history_messages, agent_type):
                messages.append({"role": "user", "content": history_prompt})

            # Add current request
            if request_msg and (request_content := getattr(request_msg, 'content', None)):
                messages.append({
                    "role": "user",
                    "content": f"{request_content}\n\nRespond with valid JSON:"
                })

            # Get and validate response
            raw_response = self._get_response(messages)
            if not raw_response:
                raise ValueError("Empty API response")
                
            return self._validate_json_response(raw_response)

        except (ValueError, ConnectionError) as e:
            logging.error(f"Query error: {str(e)}")
            return json.dumps({"type": "error", "data": {"message": str(e)}})
        except Exception as e:
            logging.exception("Unexpected query error")
            return json.dumps({"type": "error", "data": {"message": "Internal error"}})