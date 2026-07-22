import json
import concurrent.futures
from agent.llm import LLMClient
from agent.config_loader import load_config
from agent.tools import TOOL_REGISTRY

class HybridGod:
    def __init__(self):
        self.config = load_config("config.yaml")
        self.llm = LLMClient(self.config)

    def _execute_tools(self, tool_calls):
        results = {}
        def run_one(call):
            tool = call.get("tool")
            inp = call.get("input", "")
            if tool in TOOL_REGISTRY:
                return tool, TOOL_REGISTRY[tool](inp)
            return tool, f"Tool {tool} not found."

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            futures = {ex.submit(run_one, call): call for call in tool_calls}
            for f in concurrent.futures.as_completed(futures):
                tool, res = f.result()
                results[tool] = res
        return results

    def run(self, query):
        print("\n👑 GOD (Hybrid): Received task...")

        # ---- 1. PLAN: LLM decides tools ----
        plan_prompt = f"""You are Sparrow, the Planner.
User Query: {query}

Available tools: calculator, web_search, nmap, whois, dns, shell, predict_fraud, read_file, write_file.
If the user asks for factorial (like 10!), input should be "math.factorial(10)".
Output ONLY a JSON list of tool calls. Example:
[
  {{"tool": "calculator", "input": "math.factorial(10)"}},
  {{"tool": "nmap", "input": "127.0.0.1"}}
]
If no tools needed, output: []"""
        
        plan_raw = self.llm.chat([{"role": "user", "content": plan_prompt}])
        try:
            # Extract JSON from raw
            import re
            json_match = re.search(r'\[.*\]', plan_raw, re.DOTALL)
            tool_calls = json.loads(json_match.group()) if json_match else []
        except:
            tool_calls = []
        
        # ---- 2. ACT: Execute tools in parallel ----
        print("⚡ Executing tools...")
        tool_results = self._execute_tools(tool_calls) if tool_calls else {}
        
        for tool, res in tool_results.items():
            print(f"   ✅ {tool} -> {res[:100]}...")

        # ---- 3. SYNTHESIZE: LLM creates final answer with Side Panel ----
        context = "\n".join([f"{k}: {v}" for k, v in tool_results.items()]) if tool_results else "No tools used."
        
        synth_prompt = f"""You are Sparrow, the Supreme Boss.
User Query: {query}

Tool Execution Results:
{context}

Now, provide the final answer.
Format EXACTLY:

# PRIMARY SOLUTION
<The best, most correct answer>

# ALTERNATIVE OPTIONS (Side Panel)
<Option 1>
<Option 2>
<Option 3>"""
        
        final_output = self.llm.chat([{"role": "user", "content": synth_prompt}])
        return final_output

if __name__ == "__main__":
    agent = HybridGod()
    print("\n🔥 HYBRID GOD MODE (Plans + Executes + Synthesizes) - Fast & Accurate!\n")
    while True:
        q = input("You> ")
        if q.lower() in ["exit", "quit"]: break
        if not q: continue
        print(agent.run(q))
