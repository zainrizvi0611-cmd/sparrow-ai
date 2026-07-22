"""
smoke_test.py
=============

A self-contained test that exercises every non-LLLM component of the agent to
prove the wiring is correct. It does NOT require Ollama to be running.

Run:  python smoke_test.py
Exit code 0 = all checks passed.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent.config_loader import load_config  # noqa: E402
from agent.core import ReActAgent  # noqa: E402
from agent.logger import setup_logging  # noqa: E402
from agent.memory import ConversationMemory  # noqa: E402
from agent.tools import TOOL_REGISTRY  # noqa: E402
from agent.tools.calculator import calculate  # noqa: E402
from agent.tools.filesystem import configure_filesystem, read_file, write_file, append_file  # noqa: E402
from agent.tools.security import explain_vulnerability, DISCLAIMER  # noqa: E402

failures = []


def check(name: str, condition: bool, detail: str = "") -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


print("== 1. Config loading ==")
try:
    config = load_config("config.yaml")
    check("config loads", True)
    check("config.llm.model present", bool(config.llm.model), config.llm.model)
    check("config.agent.max_iterations >= 1", int(config.agent.max_iterations) >= 1)
    check("config.system_prompt non-empty", len(str(config.system_prompt)) > 100)
except Exception as exc:
    check("config loads", False, str(exc))
    sys.exit(1)

print("\n== 2. Tool registry ==")
expected = {
    "web_search", "read_file", "write_file", "append_file", "calculator",
    "security_scan", "osint_lookup", "analyze_packets", "explain_vulnerability",
}
check("all expected tools registered", expected.issubset(set(TOOL_REGISTRY)),
      f"missing: {expected - set(TOOL_REGISTRY)}")

print("\n== 3. Calculator (safe AST eval) ==")
check("basic arithmetic", calculate("2*(3+4)**2") == "Result: 98", calculate("2*(3+4)**2"))
check("math.sqrt", "Result: 4" in calculate("math.sqrt(16)"), calculate("math.sqrt(16)"))
check("alias sqrt", "Result: 4" in calculate("sqrt(16)"), calculate("sqrt(16)"))
check("log/e", "Result:" in calculate("math.log(math.e)"), calculate("math.log(math.e)"))
check("rejects dunders", "Error" in calculate("__import__('os')"), calculate("__import__('os')"))
check("rejects eval token", "Error" in calculate("eval('1+1')"), calculate("eval('1+1')"))
check("division by zero", "Error" in calculate("1/0"), calculate("1/0"))
check("trig", "Result:" in calculate("math.sin(math.pi/2)"), calculate("math.sin(math.pi/2)"))

print("\n== 4. Filesystem sandbox ==")
with tempfile.TemporaryDirectory() as tmp:
    configure_filesystem(tmp)
    w = write_file("sub/notes.txt|||hello world")
    check("write_file success", "Success" in w, w)
    r = read_file("sub/notes.txt")
    check("read_file content", r == "hello world", r[:40])
    a = append_file("sub/notes.txt|||!!!")
    check("append_file success", "Success" in a, a)
    r2 = read_file("sub/notes.txt")
    check("append reflected", r2 == "hello world!!!", r2)
    trav = read_file("../../../../etc/passwd")
    check("path traversal blocked", "outside the sandbox" in trav, trav[:60])
    trav2 = write_file("/etc/evil|||x")
    check("absolute path blocked", "absolute paths are not permitted" in trav2, trav2[:60])

print("\n== 5. Memory (sliding window + persistence) ==")
mem = ConversationMemory(window_turns=3, system_prompt="SYS")
for i in range(10):
    mem.add_message("user", f"u{i}")
    mem.add_message("assistant", f"a{i}")
hist = mem.get_history()
# window_turns=3 -> max 6 entries + 1 system = 7
check("window trimming", len(hist) == 7, f"len={len(hist)}")
check("system prompt first", hist[0]["role"] == "system")
check("oldest evicted", "u0" not in hist[1]["content"])
with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp) / "mem.json"
    mem.save_to_file(str(p))
    mem2 = ConversationMemory(window_turns=3)
    loaded = mem2.load_from_file(str(p))
    check("persistence load", loaded and mem2.size == mem.size, f"loaded={loaded} size={mem2.size}")
    check("persistence content", mem2.get_history()[1]["content"] == hist[1]["content"])

print("\n== 6. Security: explain_vulnerability + disclaimer ==")
for v in ["sqli", "xss", "csrf", "lfi", "rce", "ssrf", "xxe"]:
    out = explain_vulnerability(v)
    check(f"explain {v}", "DESCRIPTION" in out and "REMEDIATION" in out, out[:50])
bad = explain_vulnerability("notreal")
check("unknown vuln handled", "Error" in bad, bad[:60])
check("disclaimer present", "DISCLAIMER" in DISCLAIMER and "authorized" in DISCLAIMER.lower())

print("\n== 7. ReAct decision parsing (no LLM needed) ==")
# Build an agent to access _parse_decision (uses a fake config that won't connect).
cfg = load_config("config.yaml")
setup_logging(cfg)
agent = ReActAgent(cfg)
parse = agent._parse_decision
t, i, resp = parse('{"tool": "calculator", "input": "2+2"}')
check("parse tool call", t == "calculator" and i == "2+2", f"{t}|{i}|{resp}")
t, i, resp = parse('{"tool": "none", "response": "The answer is 4."}')
check("parse final answer", t == "none" and resp == "The answer is 4.", f"{t}|{resp}")
t, i, resp = parse('```json\n{"tool":"web_search","input":"cve apache"}\n```')
check("parse fenced json", t == "web_search" and i == "cve apache", f"{t}|{i}")
t, i, resp = parse('Some prose then {"tool":"none","response":"hi"} trailing')
check("parse embedded json", t == "none" and resp == "hi", f"{t}|{resp}")
t, i, resp = parse("just plain text, no json")
check("parse plain text fallback", t == "none" and resp == "just plain text, no json", f"{t}|{resp}")
t, i, resp = parse('{"tool": "unknown_thing", "input": "x"}')
check("parse unknown tool name", t == "unknown_thing", t)

print("\n== 8. Tool dispatch safety ==")
out = agent._dispatch_tool("nonexistent_tool", "x")
check("unknown tool -> error msg", "unknown tool" in out.lower(), out[:60])
out2 = agent._dispatch_tool("explain_vulnerability", "xss")
check("dispatch real tool", "DESCRIPTION" in out2, out2[:50])

print("\n" + "=" * 50)
if failures:
    print(f"RESULT: {len(failures)} FAILURE(S): {failures}")
    sys.exit(1)
else:
    print("RESULT: ALL CHECKS PASSED ✓")
    sys.exit(0)
