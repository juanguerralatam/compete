import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/chat"

payload = {
  "model": "qwen2.5",
  "messages": [
    {
      "role": "user",
      "content": "why is the sky blue?"
    }
  ],
  "stream": False
}

json_payload = json.dumps(payload)

headers = {
    'Content-Type': 'application/json'
}

try:
    response = requests.post(OLLAMA_API_URL, data=json_payload, headers=headers)
    
    response.raise_for_status()
    
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
    
except requests.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
except requests.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
except requests.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
except requests.exceptions.RequestException as err:
    print ("OOps: Something Else",err)