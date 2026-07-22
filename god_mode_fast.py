from agent.llm import LLMClient
from agent.config_loader import load_config
from agent.tools import TOOL_REGISTRY

class FastGodMode:
    def __init__(self):
        self.config = load_config("config.yaml")
        self.llm = LLMClient(self.config)

    def run(self, query):
        mega_prompt = f"""You are a Super AI with 4 expert personas inside you:
1. Researcher (Facts, Web Search) - use web_search if needed.
2. Coder (Math, Code) - use calculator.
3. Security (Nmap, Whois) - use nmap/whois.
4. Analyst (Data, Fraud) - use predict_fraud.

User Query: {query}

Provide the answer in this exact format:
---
# Researcher's Answer:
<answer>

# Coder's Answer:
<answer>

# Security's Answer:
<answer>

# Analyst's Answer:
<answer>

# PRIMARY SOLUTION (Best Path):
<best solution>

# ALTERNATIVE OPTIONS (Side Panel):
<option 1>
<option 2>
---
Use tools where necessary. Be concise and fast."""
        
        response = self.llm.chat([{"role": "user", "content": mega_prompt}])
        return response

if __name__ == "__main__":
    agent = FastGodMode()
    print("\n🔥 FAST GOD MODE (1 AI = 4 Experts) - Super Fast!\n")
    while True:
        q = input("You> ")
        if q.lower() in ["exit", "quit"]: break
        print("\n👑 GOD: " + agent.run(q))
