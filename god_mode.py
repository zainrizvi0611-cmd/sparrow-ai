import concurrent.futures
import time
from agent.llm import LLMClient
from agent.config_loader import load_config
from agent.tools import TOOL_REGISTRY

class SparrowManager:
    def __init__(self):
        self.config = load_config("config.yaml")
        self.llm = LLMClient(self.config)
        self.boss_llm = LLMClient(self.config)

        self.agents = [
            {"name": "Researcher", "role": "You are a Research Agent. Use 'web_search' for facts.", "tools": ["web_search"]},
            {"name": "Coder", "role": "You are a Coding Agent. Use 'calculator' and 'write_file'.", "tools": ["calculator", "write_file"]},
            {"name": "Security", "role": "You are a Security Agent. Use 'nmap', 'whois', 'dns', 'shell'.", "tools": ["nmap", "whois", "dns", "shell"]},
            {"name": "Analyst", "role": "You are a Data Analyst. Use 'predict_fraud' and 'read_file'.", "tools": ["predict_fraud", "read_file"]}
        ]

    def _execute_tool(self, tool_name, input_str):
        if tool_name in TOOL_REGISTRY:
            return TOOL_REGISTRY[tool_name](input_str)
        return f"Tool {tool_name} not available."

    def run(self, query):
        print(f"\n👑 GOD (Supreme Boss): Received task: '{query}'")
        print("⚡ Delegating to 4 Powerful Experts...\n")

        plan_prompt = f"""You are God, the Supreme Manager.
Split the query into 4 specific sub-tasks for these Experts:
1. Researcher (Facts, News, Web).
2. Coder (Math, Logic, Code).
3. Security (Networks, Ports, Domains).
4. Analyst (Fraud, Data, Files).

Query: {query}
Output exactly 4 lines (one for each). No extra text."""
        plan = self.llm.chat([{"role": "user", "content": plan_prompt}])
        tasks = plan.strip().split('\n')
        while len(tasks) < 4: tasks.append("Analyze context.")

        results = {}
        def execute_agent(agent, task):
            print(f"⚡ {agent['name']} is working...")
            try:
                tool_prompt = f"{agent['role']}\nTask: {task}\n\nTools: {agent['tools']}. If need tool: TOOL_CALL: <tool>|<input>"
                initial_res = self.llm.chat([{"role": "user", "content": tool_prompt}])
                if "TOOL_CALL:" in initial_res:
                    parts = initial_res.split("TOOL_CALL:")[1].strip().split("|", 1)
                    if len(parts) == 2:
                        t_name, t_input = parts[0].strip(), parts[1].strip()
                        print(f"   🛠️ {agent['name']} calling {t_name}...")
                        tool_output = self._execute_tool(t_name, t_input)
                        final_prompt = f"Tool returned: {tool_output}\n\nNow provide final answer."
                        final_res = self.llm.chat([{"role": "user", "content": final_prompt}])
                        return agent['name'], final_res
                return agent['name'], initial_res
            except Exception as e:
                return agent['name'], f"Error: {e}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(execute_agent, agent, tasks[i]): i for i, agent in enumerate(self.agents)}
            for future in concurrent.futures.as_completed(futures):
                name, result = future.result()
                results[name] = result
                print(f"✅ {name} finished.")

        print("\n👑 GOD: Cross-checking everything...")
        combined = "\n".join([f"--- {name} ---\n{res}" for name, res in results.items()])
        
        synthesis_prompt = f"""God, you are the Supreme Boss.
Sub-Experts Results:
{combined}

User Query: {query}

Format:
# PRIMARY SOLUTION
<Best answer>

# ALTERNATIVE OPTIONS (Side Panel)
<Option 1>
<Option 2>
<Option 3>"""
        final_output = self.boss_llm.chat([{"role": "user", "content": synthesis_prompt}])
        
        print("\n" + "="*50)
        print("👑 GOD MODE FINAL OUTPUT")
        print("="*50)
        return final_output

if __name__ == "__main__":
    manager = SparrowManager()
    print("\n🔥 GOD MODE ACTIVATED. Type 'exit' to quit.\n")
    while True:
        q = input("You> ")
        if q.lower() in ["exit", "quit"]: break
        if not q: continue
        print(manager.run(q))
