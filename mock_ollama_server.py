"""
mock_ollama_server.py
=====================

A tiny HTTP server that mimics Ollama's OpenAI-compatible
``/v1/chat/completions`` endpoint for end-to-end testing of the ReAct loop
WITHOUT needing a real LLM or Ollama installed.

It inspects the last user/tool message in the request and emits canned but
*valid* JSON decisions that drive the agent through a real multi-step tool
sequence, then a final answer. This proves the full Plan->Act->Observe->Respond
cycle works against real tool output.

Run:   python mock_ollama_server.py --port 11435
Point the agent at it via config: llm.endpoint = http://localhost:11435/v1/chat/completions
"""

from __future__ import annotations

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def _decide(messages):
    """
    Produce a canned JSON decision based on the latest non-system message.

    The mock "reasons" about the conversation so far:
      - If the user asks for a web search -> call web_search, then answer.
      - If the user asks to calculate -> call calculator, then answer.
      - If the user asks to write a file -> call write_file, then answer.
      - If the user asks to explain a vuln -> call explain_vulnerability, then answer.
      - If the last message is a tool observation -> synthesize a final answer
        referencing that observation (this is the Respond step).
    """
    # Find the most recent user or tool message content.
    last_user = None
    last_tool_obs = None
    for m in messages:
        if m["role"] == "user":
            last_user = m["content"]
            last_tool_obs = None  # reset; a new user turn starts fresh
        elif m["role"] == "tool":
            last_tool_obs = m["content"]

    # If we just observed a tool result, produce a final answer (Respond).
    if last_tool_obs is not None and last_user is not None:
        # A real LLM would synthesize a natural answer from the observation.
        # The mock keeps a generous slice of the observation so the full tool
        # output (e.g. vulnerability name, numeric result, success message)
        # is reflected in the final answer.
        snippet = last_tool_obs.replace("\n", " ").strip()
        # Strip the leading "[Tool '...' output]" wrapper for a cleaner answer.
        snippet = re.sub(r"^\[Tool '[^']+' output\]\s*", "", snippet)
        if len(snippet) > 600:
            snippet = snippet[:600] + "..."
        return {
            "tool": "none",
            "response": (
                f"Based on my reasoning and the tool observation, here is my answer: "
                f"{snippet}"
            ),
        }

    # Otherwise, decide which tool to call (Plan + Act).
    q = (last_user or "").lower()

    if "search" in q or "web" in q or "latest" in q or "news" in q or "cve" in q:
        # Derive a reasonable query from the user text.
        query = re.sub(r"[?.!]+$", "", last_user or "").strip()
        return {"tool": "web_search", "input": query}

    if "calc" in q or any(ch in q for ch in ["+", "*", "/", "sqrt", "log", "power of", "squared"]):
        # Extract a clean math expression: strip leading verbs/words and
        # trailing pleasantries, keep only math characters, names, parens.
        expr = last_user or ""
        # Remove common leading words: "Calculate", "compute", "what is", "the", etc.
        expr = re.sub(r"^(?:please\s+)?(?:calculate|compute|what(?:'s| is)|evaluate|solve)\s+", "", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\s+(?:please|for me|thanks|thank you)\s*[?.!]*$", "", expr, flags=re.IGNORECASE)
        expr = expr.strip().rstrip("?.!")
        # Map common words to math operators/functions.
        expr = expr.replace("squared", "**2").replace("square root of", "sqrt")
        expr = expr.replace(" to the power of ", "**")
        # Validate it contains at least one digit, else fall back.
        if not re.search(r"\d", expr):
            expr = "2+2"
        return {"tool": "calculator", "input": expr.strip()}

    if "write" in q and "file" in q:
        # Parse "write a file called X with the text Y"
        path_match = re.search(r"(?:called|named)\s+(\S+\.?\S*)", q)
        path = path_match.group(1) if path_match else "output.txt"
        text_match = re.search(r"(?:text|content)\s+['\"]?(.*?)['\"]?\s*$", last_user or "", re.IGNORECASE)
        content = text_match.group(1) if text_match else "sample content"
        return {"tool": "write_file", "input": f"{path}|||{content}"}

    if "read" in q and "file" in q:
        path_match = re.search(r"(?:called|named|read)\s+(\S+\.?\S*)", q)
        path = path_match.group(1) if path_match else "notes.txt"
        return {"tool": "read_file", "input": path}

    if "explain" in q and ("vuln" in q or "injection" in q or "xss" in q or "sqli" in q
                           or "csrf" in q or "rce" in q or "ssrf" in q or "xxe" in q or "lfi" in q):
        vmap = {"injection": "sqli", "sqli": "sqli", "sql": "sqli",
                "xss": "xss", "csrf": "csrf", "rce": "rce",
                "ssrf": "ssrf", "xxe": "xxe", "lfi": "lfi"}
        vt = "sqli"
        for k, v in vmap.items():
            if k in q:
                vt = v
                break
        return {"tool": "explain_vulnerability", "input": vt}

    if "hello" in q or "hi" in q or "who are you" in q:
        return {"tool": "none", "response": "Hello! I'm SuperNinja, an autonomous ReAct AI agent. How can I help you today?"}

    # Default: answer directly.
    return {"tool": "none", "response": f"I considered your request: '{last_user}'. (mock response)"}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if not self.path.startswith("/v1/chat/completions"):
            self._send(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._send(400, {"error": "invalid json"})
            return
        messages = payload.get("messages", [])
        decision = _decide(messages)
        # Return OpenAI-shaped chat completion with the JSON decision as content.
        resp = {
            "id": "chatcmpl-mock",
            "object": "chat.completion",
            "model": payload.get("model", "mock"),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": json.dumps(decision)},
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }
        self._send(200, resp)

    def do_GET(self):
        # Minimal health/models endpoints for compatibility.
        if self.path == "/api/tags" or self.path == "/v1/models":
            self._send(200, {"models": [{"name": "mock-llm"}]})
        else:
            self._send(200, {"status": "ok"})

    def log_message(self, *args):
        pass  # silence default stderr logging


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=11435)
    p.add_argument("--host", default="127.0.0.1")
    args = p.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Mock Ollama server on http://{args.host}:{args.port}/v1/chat/completions")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
