import requests
import json
import sys

class LLMClient:
    def __init__(self, config):
        self.provider = config['llm'].get('provider', 'ollama')
        self.endpoint = config['llm'].get('endpoint', 'http://127.0.0.1:11434/v1/chat/completions')
        self.model = config['llm'].get('model', 'llama3.2:1b')
        self.api_key = config['llm'].get('api_key', '')
        self.timeout = config['llm'].get('timeout', 120)

    def chat(self, messages):
        try:
            if self.provider == "openai":
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {"model": self.model, "messages": messages}
                resp = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=self.timeout)
            elif self.provider == "gemini":
                # Simulate Gemini via endpoint
                resp = requests.post(self.endpoint, json={"model": self.model, "messages": messages}, timeout=self.timeout)
            else:  # ollama default
                resp = requests.post(self.endpoint, json={"model": self.model, "messages": messages}, timeout=self.timeout)
            
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                raise Exception(f"API Error {resp.status_code}: {resp.text}")
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Cannot reach {self.provider} at {self.endpoint}")
            sys.exit(1)
        except Exception as e:
            raise e
