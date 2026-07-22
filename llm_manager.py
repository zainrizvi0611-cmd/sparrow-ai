import requests
import json

class LLMManager:
    def __init__(self, config):
        self.provider = config.LLM_PROVIDER
        self.endpoint = config.OLLAMA_ENDPOINT
        self.model = config.OLLAMA_MODEL
    
    def chat(self, messages, lang='en'):
        try:
            if self.provider == "ollama":
                return self._ollama_chat(messages)
            elif self.provider == "openai":
                return self._openai_chat(messages)
            elif self.provider == "gemini":
                return self._gemini_chat(messages)
        except Exception as e:
            return f"[LLM Error] {e}"
    
    def _ollama_chat(self, messages):
        resp = requests.post(
            self.endpoint,
            json={"model": self.model, "messages": messages, "stream": False},
            timeout=120
        )
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        raise Exception(f"Ollama Error: {resp.status_code}")
    
    def _openai_chat(self, messages):
        return "OpenAI Not Configured"
    
    def _gemini_chat(self, messages):
        return "Gemini Not Configured"
