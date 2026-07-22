import re
import math
import concurrent.futures
from agent.llm import LLMClient
from agent.config_loader import load_config
from agent.tools import TOOL_REGISTRY

class NoRefusalGod:
    def __init__(self):
        self.config = load_config("config.yaml")
        self.llm = LLMClient(self.config)

    def _compute_factorial(self, num):
        return str(math.factorial(num))

    def _extract_commands(self, query):
        commands = []
        
        # Factorial: "calculate 10!" or "10!" 
        fact_match = re.search(r'(\d+)!', query)
        if fact_match:
            num = int(fact_match.group(1))
            commands.append({"tool": "calculator", "input": str(num)})  # we'll handle separately
            # We'll store the number separately to compute factorial directly
            self._factorial_num = num
        else:
            self._factorial_num = None

        # Nmap scan
        if "scan" in query or "localhost" in query or "nmap" in query:
            commands.append({"tool": "nmap", "input": "127.0.0.1"})

        # Web Search
        if "tell me about" in query.lower() or "search" in query.lower() or "news" in query.lower():
            match = re.search(r'(?:tell me about|search for|search)\s+(.+)', query, re.IGNORECASE)
            if match:
                commands.append({"tool": "web_search", "input": match.group(1)})
            else:
                commands.append({"tool": "web_search", "input": query[:50]})

        # Fraud prediction
        if "fraud" in query or "predict" in query:
            commands.append({"tool": "predict_fraud", "input": "0.1, -0.02, 0.5, 1.2, 0.8"})

        return commands

    def _execute_tools(self, commands):
        results = {}
        
        # Special handling for factorial
        if hasattr(self, '_factorial_num') and self._factorial_num is not None:
            # Compute factorial directly
            results["factorial"] = f"{self._factorial_num}! = {math.factorial(self._factorial_num)}"
            # Remove calculator command if exists
            commands = [cmd for cmd in commands if cmd.get("tool") != "calculator"]

        def run_one(cmd):
            tool = cmd.get("tool")
            inp = cmd.get("input")
            if tool in TOOL_REGISTRY:
                return tool, TOOL_REGISTRY[tool](inp)
            return tool, "Tool not found."

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            futures = {ex.submit(run_one, cmd): cmd for cmd in commands}
            for f in concurrent.futures.as_completed(futures):
                tool, res = f.result()
                results[tool] = res
        return results

    def run(self, query):
        print("\n👑 GOD (No Refusal): Directly executing tools...")
        commands = self._extract_commands(query)
        if not commands:
            return "No specific tools detected. Please ask something like 'calculate 10!' or 'scan localhost'."

        print("⚡ Running tools directly (NO LLM PLANNER, NO REFUSALS!)...")
        results = self._execute_tools(commands)

        output = "# PRIMARY SOLUTION (Direct Tool Results)\n"
        for tool, res in results.items():
            output += f"✅ {tool.upper()}: {res}\n"

        output += "\n# ALTERNATIVE OPTIONS (Side Panel)\n"
        output += "- For more details, add 'verbose' to your query\n"
        output += "- Use `shell` to run custom commands\n"
        output += "- Try 'scan 127.0.0.1 -p 80' for specific ports\n"
        return output

if __name__ == "__main__":
    agent = NoRefusalGod()
    print("\n🔥 FINAL GOD MODE (Zero Refusals - Pure Tool Execution)\n")
    while True:
        q = input("You> ")
        if q.lower() in ["exit", "quit"]: break
        if not q: continue
        print(agent.run(q))
