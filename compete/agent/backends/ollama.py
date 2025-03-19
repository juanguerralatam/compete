import os
import re
import json
import logging
import requests
from typing import List
from tenacity import retry, stop_after_attempt, wait_random_exponential

from .base import IntelligenceBackend
from ...message import Message

DEFAULT_TEMPERATURE = 0.9
DEFAULT_MAX_TOKENS = 1024
END_OF_MESSAGE = "<EOS>"
STOP = ("", END_OF_MESSAGE)
BASE_PROMPT = f"The messages always end with the token {END_OF_MESSAGE}."

OLLAMA_API_URL = "http://localhost:11434/api/chat"

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
    def _get_response(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        headers = {
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(OLLAMA_API_URL, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            
            try:
                response_data = response.json()
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON response from Ollama API: {response.text}")
                
            if not isinstance(response_data, dict):
                raise ValueError(f"Expected dict response, got {type(response_data)}")
                
            if 'message' not in response_data:
                raise ValueError(f"Response missing 'message' field: {response_data}")
                
            if 'content' not in response_data['message']:
                raise ValueError(f"Response message missing 'content' field: {response_data['message']}")
                
            content = response_data['message']['content']
            if not isinstance(content, str):
                raise ValueError(f"Expected string content, got {type(content)}")
                
            return content
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama API: {str(e)}")


    def query(self, agent_name: str, agent_type: str, role_desc: str, history_messages: List[Message],
              global_prompt: str = None, request_msg: Message = None, *args, **kwargs) -> str:
        # Enhanced system prompt with scene context
        system_prompt = f"""You are {agent_name}.
        Your responses MUST be in JSON format ONLY. Follow this template:
        {{
            "type": "<action_type>",
            "data": {{
                // Your content here
            }}
        }}
        Do NOT include any additional text, explanations, or markdown formatting.
        Ensure your response is a valid JSON object with the exact structure shown above.
        Any deviation from this format will cause errors in scene processing."""
        
        # Validate and handle request message
        user_prompt = ""
        if request_msg and hasattr(request_msg, 'content'):
            content = request_msg.content if request_msg.content is not None else ""
            user_prompt = f"{content}\n\nRespond ONLY with valid JSON using the specified format."
        else:
            user_prompt = "Respond ONLY with valid JSON using the specified format."
        
        messages = []
        
        try:
            # Validate input parameters
            if not agent_name or not isinstance(agent_name, str):
                raise ValueError("Invalid agent_name parameter")
            if not role_desc or not isinstance(role_desc, str):
                raise ValueError("Invalid role_desc parameter")
            if history_messages is not None and not isinstance(history_messages, list):
                raise ValueError("Invalid history_messages parameter")
            
            # Construct system prompt
            system_prompt = f"Your name is {agent_name}.\n\nYour role:{role_desc}"
            if global_prompt:
                if not isinstance(global_prompt, str):
                    raise ValueError("Invalid global_prompt parameter")
                system_prompt = f"{global_prompt.strip()}\n\n" + system_prompt
            system_prompt += f"\n\n{BASE_PROMPT}"
            
            system_message = {"role": "system", "content": system_prompt}
            messages.append(system_message)
            
            # Process history messages
            if history_messages:
                user_messages = []
                if len(history_messages) > 12:
                    history_messages = history_messages[-12:]
                for msg in history_messages:
                    if not hasattr(msg, 'agent_name') or not hasattr(msg, 'content'):
                        continue
                    content = str(msg.content) if msg.content is not None else ""
                    user_messages.append((msg.agent_name, f"{content}{END_OF_MESSAGE}"))

                user_prompt = ""
                for _, msg in enumerate(user_messages):
                    user_prompt += f"[{msg[0]}]: {msg[1]}\n"
                user_prompt += f"You are a {agent_type} in a virtual world. Respond with a valid JSON object following the specified format. Now it's your turn!"
                
                user_message = {"role": "user", "content": user_prompt}
                messages.append(user_message)

            # Add user message to messages list
            if user_prompt:
                user_message = {"role": "user", "content": user_prompt}
                messages.append(user_message)
            else:
                raise ValueError("Empty user prompt")

            # Get response from API
            try:
                response = self._get_response(messages)
                if not response:
                    raise ValueError("Empty response from Ollama API")
                logging.info(f"Successfully received response from Ollama API for {agent_name}")
            except Exception as e:
                logging.error(f"Failed to get response from Ollama API for {agent_name}: {str(e)}")
                raise
                
            # Clean up response format and ensure proper JSON structure
            response = re.sub(rf"^\s*\[.*]:", "", response).strip()
            response = re.sub(rf"^\s*{re.escape(agent_name)}\s*:", "", response).strip()
            response = re.sub(rf"{END_OF_MESSAGE}$", "", response).strip()
            
            # Validate and format JSON response
            try:
                response_json = json.loads(response)
                if not isinstance(response_json, dict):
                    response_json = {"type": "text", "data": response_json}
                elif "type" not in response_json or "data" not in response_json:
                    response_json = {"type": "text", "data": response_json}
                response = json.dumps(response_json)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format in response")
            
            if not response:
                raise ValueError("Empty response after cleanup")
            
            # Validate response format and ensure proper JSON structure
            try:
                # Try to parse and validate JSON structure
                if response.strip().startswith('{') and response.strip().endswith('}'):
                    parsed_json = json.loads(response)
                    if not isinstance(parsed_json, dict) or 'type' not in parsed_json or 'data' not in parsed_json:
                        raise ValueError("Response must be a JSON object with 'type' and 'data' fields")
                    if not isinstance(parsed_json['data'], dict):
                        raise ValueError("The 'data' field must be a JSON object")
                    response = json.dumps(parsed_json)  # Normalize JSON format
                else:
                    raise ValueError("Response must be a JSON object")
            except (json.JSONDecodeError, ValueError) as e:
                error_msg = f"Invalid JSON format: {str(e)}"
                logging.error(error_msg)
                raise ValueError(error_msg)
            
            return response
            
        except (ValueError, ConnectionError) as e:
            error_msg = f"Failed to get valid response: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in query: {str(e)}"
            logging.error(error_msg)
            raise RuntimeError(error_msg)