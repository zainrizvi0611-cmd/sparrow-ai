import json
import re
from agent.llm import LLMClient
from agent.memory import Memory
from agent.tools import TOOL_REGISTRY

class ReActAgent:
    def __init__(self, config):
        self.config = config
        self.llm = LLMClient(config)
        self.memory = Memory(window_turns=config['memory']['window_turns'])
        self.max_iterations = config['agent'].get('max_iterations', 5)
        self.workspace = config['filesystem'].get('sandbox_dir', './agent_workspace')
        self.logger = None

    def set_logger(self, logger):
        self.logger = logger

    def _log(self, level, msg):
        if self.logger:
            getattr(self.logger, level)(msg)

    def run(self, query):
        self.memory.add_message("user", query)
        
        # --- FAST PATH: Direct tool execution ---
        tool_match = None
        tool_input = ""

        if query.startswith("calc"):
            expr = query[len("calc"):].strip()
            if expr:
                tool_match = "calculator"
                tool_input = expr

        elif query.startswith("write_file"):
            if " with content " in query:
                parts = query.split(" with content ", 1)
                filename = parts[0].replace("write_file", "").strip()
                content = parts[1].strip()
                if filename and content:
                    tool_match = "write_file"
                    tool_input = {"filename": filename, "content": content}

        elif query.startswith("read_file"):
            filename = query[len("read_file"):].strip()
            if filename:
                tool_match = "read_file"
                tool_input = filename

        elif query.startswith("web_search"):
            q = query[len("web_search"):].strip()
            if q:
                tool_match = "web_search"
                tool_input = q

        elif query.startswith("append_file"):
            if " with content " in query:
                parts = query.split(" with content ", 1)
                filename = parts[0].replace("append_file", "").strip()
                content = parts[1].strip()
                if filename and content:
                    tool_match = "append_file"
                    tool_input = {"filename": filename, "content": content}

        elif query.startswith("explain"):
            vuln = query[len("explain"):].strip()
            if vuln:
                tool_match = "explain_vulnerability"
                tool_input = vuln

        # HACKING TOOLS
        elif query.startswith("nmap"):
            target = query[len("nmap"):].strip()
            if target:
                tool_match = "nmap"
                tool_input = target

        elif query.startswith("whois"):
            domain = query[len("whois"):].strip()
            if domain:
                tool_match = "whois"
                tool_input = domain

        elif query.startswith("dns"):
            domain = query[len("dns"):].strip()
            if domain:
                tool_match = "dns"
                tool_input = domain

        elif query.startswith("hash_crack"):
            h = query[len("hash_crack"):].strip()
            if h:
                tool_match = "hash_crack"
                tool_input = h

        elif query.startswith("http_req"):
            url = query[len("http_req"):].strip()
            if url:
                tool_match = "http_req"
                tool_input = url

        elif query.startswith("shell"):
            cmd = query[len("shell"):].strip()
            if cmd:
                tool_match = "shell"
                tool_input = cmd

        # ========== NEW FRAUD TOOL FAST PATH ==========
        elif query.startswith("predict_fraud"):
            features = query[len("predict_fraud"):].strip()
            if features:
                tool_match = "predict_fraud"
                tool_input = features

        # Execute Fast Path
        if tool_match:
            self._log("info", f"Fast path: {tool_match}")
            try:
                if tool_match not in TOOL_REGISTRY:
                    return f"Error: Tool '{tool_match}' not found."
                result = TOOL_REGISTRY[tool_match](tool_input)
                self.memory.add_message("assistant", str(result))
                return str(result)
            except Exception as e:
                self._log("error", f"Fast path error: {e}")
                return f"Error: {e}"

        # --- STANDARD REACT LOOP (Fallback) ---
        context = self.memory.get_history()
        for i in range(self.max_iterations):
            self._log("info", f"ReAct loop {i+1}/{self.max_iterations}")
            tools_list = list(TOOL_REGISTRY.keys())
            
            plan_prompt = f"""You are a ReAct agent. 
Tools: {tools_list}
Output ONLY JSON. Examples:
{{"tool": "calculator", "input": "2+2"}}
{{"tool": "nmap", "input": "127.0.0.1"}}
{{"tool": "predict_fraud", "input": "0.1, -0.02,..."}}
{{"tool": "none", "response": "Final answer"}}

User: {query}
Context: {context[-2:]}
JSON:"""
            
            try:
                raw = self.llm.chat([{"role": "user", "content": plan_prompt}])
                json_match = re.search(r'\{.*\}', raw, re.DOTALL)
                if not json_match:
                    continue
                decision = json.loads(json_match.group())
                
                if decision.get("tool") == "none":
                    return decision.get("response", "No answer.")
                
                t_name = decision.get("tool")
                t_input = decision.get("input", "")
                
                if t_name not in TOOL_REGISTRY:
                    return f"Tool '{t_name}' not found."
                
                result = TOOL_REGISTRY[t_name](t_input)
                self.memory.add_message("assistant", str(result))
                return str(result)
            
            except:
                continue
        
        return "Max iterations reached. Please rephrase."

    def save_session(self):
        self.memory.save_to_file("agent_workspace/session_memory.json")

    def load_session(self):
        return self.memory.load_from_file("agent_workspace/session_memory.json")
