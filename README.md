# SuperNinja — Autonomous ReAct AI Agent

A production-ready, modular autonomous AI agent built on the **ReAct (Reasoning + Acting)** loop architecture. It integrates **local LLM inference** via [Ollama](https://ollama.com), **multiple tools** (web search, sandboxed file I/O, a safe calculator, and a cybersecurity toolkit), **persistent sliding-window memory**, and **structured rotating logging**.

> ⚠️ **MANDATORY DISCLAIMER** ⚠️
>
> This toolkit is intended exclusively for authorized security research, ethical penetration testing, and educational purposes on systems you own or have explicit written permission to test. Unauthorized use against systems you do not own is illegal and unethical. The developer assumes no liability for misuse.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Setup & Installation](#setup--installation)
4. [Configuration](#configuration)
5. [Running the Agent](#running-the-agent)
6. [Example Interactions](#example-interactions)
7. [Module Reference](#module-reference)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Ethical Use](#ethical-use)

---

## Architecture Overview

The agent implements a strict **Plan → Act → Observe → Respond** cycle:

```
        ┌─────────────────────────────────────────────────────────┐
        │                      USER QUERY                         │
        └────────────────────────────┬────────────────────────────┘
                                     ▼
        ┌─────────────────────────────────────────────────────────┐
        │  PLAN   — LLM receives (system prompt + history + user) │
        │           and reasons about which tool (if any) to call │
        │           Output: JSON decision                         │
        │             {"tool": "<name>", "input": "<input>"}      │
        │             {"tool": "none", "response": "<answer>"}    │
        └────────────────────────────┬────────────────────────────┘
                                     ▼
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
          {"tool": "none"}                  {"tool": "<name>"}
                    │                                 │
                    ▼                                 ▼
              ┌──────────┐                   ┌───────────────┐
              │ RESPOND  │                   │  ACT          │
              │ (final)  │                   │  dispatch tool│
              └──────────┘                   └───────┬───────┘
                                                     ▼
                                            ┌────────────────┐
                                            │  OBSERVE       │
                                            │  append output │
                                            │  to memory     │
                                            └───────┬────────┘
                                                    │
                                     ┌──────────────┘
                                     ▼
                          (loop back to PLAN, up to max_iterations)
```

- **Multi-step reasoning**: the agent may chain several tool calls before producing a final answer.
- **Loop guard**: `max_iterations` (default 10) prevents infinite tool-calling.
- **Tool output as observation**: every tool result is fed back as a `tool`-role message so the LLM reasons over real data.

---

## Project Structure

```
.
├── main.py                      # CLI entry point (REPL + single-shot modes)
├── config.yaml                  # All configurable parameters
├── requirements.txt             # Python dependencies
├── README.md                    # This guide
├── smoke_test.py                # Component-level verification suite
├── e2e_test.py                  # End-to-end ReAct loop test
├── mock_ollama_server.py        # Mock LLM server for testing without Ollama
└── agent/
    ├── __init__.py
    ├── config_loader.py         # Loads + validates config.yaml (dot-access)
    ├── logger.py                # Rotating structured logging
    ├── memory.py                # Sliding-window conversation buffer + JSON persistence
    ├── llm.py                   # Ollama (OpenAI-compatible) client with error handling
    ├── core.py                  # The ReAct loop + tool dispatcher
    └── tools/
        ├── __init__.py          # Tool registry (name -> callable)
        ├── search.py            # DuckDuckGo web search (retry, rate-limit aware)
        ├── filesystem.py        # Sandboxed read/write/append (path-traversal safe)
        ├── calculator.py        # Safe AST-based math evaluator
        └── security.py          # nmap/sqlmap/gobuster/nikto + OSINT + scapy + vuln explain
```

---

## Setup & Installation

### Step 1 — Install Ollama

Ollama runs a local LLM server with an OpenAI-compatible API.

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
# Option A: Homebrew
brew install ollama
# Option B: Download the app from https://ollama.com/download
```

**Windows:**
Download the installer from [https://ollama.com/download](https://ollama.com/download) and run it.

### Step 2 — Start the Ollama server & pull a model

Open a terminal and start the server (it stays running in the foreground):
```bash
ollama serve
```

In a **second** terminal, pull a model (one-time download, ~2–5 GB depending on model):
```bash
# Recommended default (small, fast, capable):
ollama pull llama3.2

# Alternatives (edit config.yaml -> llm.model to switch):
ollama pull qwen2.5
ollama pull mistral
ollama pull phi3
ollama pull gemma2
```

Verify it works:
```bash
ollama run llama3.2 "Say hello in one sentence."
```

The server listens on `http://localhost:11434` by default.

### Step 3 — Set up the Python environment

```bash
# Clone or cd into the project directory
cd react-agent

# Create a virtual environment (Python 3.10+)
python3 -m venv .venv

# Activate it
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows (PowerShell)

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4 — Install system-level security tools (optional, only for the security toolkit)

The security tools (`nmap`, `sqlmap`, `gobuster`, `nikto`) are external CLIs invoked via `subprocess` — they are **not** pip packages.

**Debian / Ubuntu:**
```bash
sudo apt update
sudo apt install -y nmap sqlmap nikto gobuster libpcap-dev
```

**macOS (Homebrew):**
```bash
brew install nmap libpcap
pip install sqlmap          # sqlmap is pip-installable too
# gobuster:  brew install gobuster  (or: go install github.com/OJ/gobuster/v3@latest)
# nikto:     git clone https://github.com/sullo/nikto && cd nikto && perl nikto.pl -h
```

**Scapy** (for `analyze_packets`) also needs `libpcap`:
- Linux: `sudo apt install libpcap-dev`
- macOS: `brew install libpcap`
- Live packet capture requires root/sudo or `CAP_NET_RAW`.

### Step 5 — Configure the agent

Edit `config.yaml`. The most important fields:

```yaml
llm:
  endpoint: "http://localhost:11434/v1/chat/completions"
  model: "llama3.2"          # must match a model you pulled
  timeout: 120

agent:
  max_iterations: 10

memory:
  window_turns: 20
  persistence_file: "agent_workspace/session_memory.json"

filesystem:
  sandbox_dir: "agent_workspace"   # all file ops confined here

security:
  subprocess_timeout: 60
  shodan_api_key: null              # optional: get one at shodan.io
  default_packet_count: 20
```

See the [Configuration](#configuration) section for every option.

### Step 6 — Run the agent

Make sure `ollama serve` is running in another terminal, then:

```bash
python main.py
```

You'll see the startup banner with the ethics disclaimer, then the REPL prompt:

```
========================================================================
  SuperNinja — Autonomous ReAct AI Agent
  Model: llama3.2    Endpoint: http://localhost:11434/v1/chat/completions
  ...
  DISCLAIMER: This toolkit is intended exclusively for authorized ...
========================================================================

You>
```

Type a request and press Enter. Type `exit` to quit, `clear` to wipe memory, `help` for commands.

---

## Configuration

All parameters live in `config.yaml`. Missing keys fall back to sane defaults (see `agent/config_loader.py`).

| Section | Key | Default | Description |
|---------|-----|---------|-------------|
| `llm` | `endpoint` | `http://localhost:11434/v1/chat/completions` | Ollama OpenAI-compatible URL |
| `llm` | `model` | `llama3.2` | Ollama model tag |
| `llm` | `temperature` | `0.7` | Sampling temperature |
| `llm` | `max_tokens` | `null` | Cap on generated tokens (null = model default) |
| `llm` | `timeout` | `120` | Per-request timeout (seconds) |
| `llm` | `top_p` | `0.9` | Nucleus sampling |
| `agent` | `max_iterations` | `10` | ReAct loop iteration cap |
| `memory` | `window_turns` | `20` | Sliding window size (turns) |
| `memory` | `persistence_file` | `agent_workspace/session_memory.json` | Session save path (`null` disables) |
| `filesystem` | `sandbox_dir` | `agent_workspace` | Sandboxed file root |
| `search` | `max_results` | `5` | DuckDuckGo result count |
| `search` | `max_retries` | `2` | Retries on rate-limit |
| `search` | `retry_delay` | `2` | Seconds between retries |
| `security` | `subprocess_timeout` | `60` | CLI tool timeout |
| `security` | `shodan_api_key` | `null` | Optional Shodan key |
| `security` | `default_packet_count` | `20` | Default packets to capture |
| `logging` | `log_dir` | `logs` | Log directory |
| `logging` | `console_level` | `INFO` | Console log level |
| `logging` | `file_level` | `DEBUG` | File log level |
| `logging` | `max_bytes` | `5242880` | 5 MB rotation size |
| `logging` | `backup_count` | `3` | Rotated backups kept |
| `logging` | `filename` | `agent.log` | Log file name |
| `system_prompt` | — | *(inline)* | The LLM system prompt |

---

## Running the Agent

### Interactive REPL (default)

```bash
python main.py
```

Commands inside the REPL:
- `exit` / `quit` — leave the agent
- `clear` — wipe conversation memory
- `help` — show available commands

### Single-shot mode

```bash
python main.py --once "Explain the XSS vulnerability"
```

### Custom config file

```bash
python main.py --config /path/to/my_config.yaml
```

---

## Example Interactions

### Example 1 — Web Search

```
You> Search the web for the latest Python release notes

Agent> Here's what I found regarding the latest Python release:

  [1] What's New In Python 3.x
      URL: https://docs.python.org/3/whatsnew/3.x.html
      This article explains the new features in Python 3.x ...
  [2] Python Release Schedule
      URL: https://peps.python.org/pep-0664/
      ...
```

Under the hood the agent emits `{"tool": "web_search", "input": "latest Python release notes"}`, the DuckDuckGo tool returns formatted results, the agent observes them, then produces a final natural-language summary.

### Example 2 — File Operations

```
You> Write a file called report.md with the text "# Recon Report\nTarget authorized for testing."

Agent> Done — I wrote the file `report.md` inside the sandbox with that content.

You> Now read it back to me.

Agent> The file contains:
  # Recon Report
  Target authorized for testing.
```

File operations are confined to `agent_workspace/`. Path traversal (`../../etc/passwd`) and absolute paths (`/etc/hosts`) are rejected.

### Example 3 — Security Tool Invocation

```
You> I own and am authorized to test 127.0.0.1. Run an nmap service scan on it.

Agent> [runs nmap -sV 127.0.0.1 via subprocess, then summarizes the open ports and services detected]
```

The agent emits `{"tool": "security_scan", "input": "nmap|-sV 127.0.0.1"}`. Output is prefixed with the ethics disclaimer. If the tool isn't installed, you get a clear install hint instead of a crash.

### Example 4 — Calculator

```
You> Calculate 2*(3+4)**2 + math.sqrt(16)

Agent> Result: 102
```

The expression is evaluated via a safe AST walker — no `eval`, no arbitrary attribute access.

### Example 5 — Vulnerability Explanation

```
You> Explain the SSRF vulnerability

Agent> [returns a structured write-up: description, attack vector, example payload, remediation]
```

Supported types: `sqli`, `xss`, `csrf`, `lfi`, `rce`, `ssrf`, `xxe`.

---

## Module Reference

### `agent/core.py` — ReAct Loop

`ReActAgent.run(user_input)` drives the cycle:
1. **Plan**: sends memory history to the LLM; parses the JSON decision.
2. **Act**: dispatches the named tool via `TOOL_REGISTRY`.
3. **Observe**: appends tool output as a `tool`-role message.
4. **Respond**: when the LLM emits `{"tool": "none", "response": ...}`, returns it.

Decision parsing is defensive: strips markdown fences, extracts the first balanced `{...}`, tolerates missing keys, and falls back to treating raw text as a final answer.

### `agent/tools/search.py` — Web Search

`web_search(query)` uses `ddgs` (current) or `duckduckgo_search` (legacy), returns 3–5 formatted results, retries on rate-limit errors (configurable), never raises.

### `agent/tools/filesystem.py` — Sandboxed File I/O

`read_file`, `write_file`, `append_file` — all paths are resolved relative to the sandbox and validated against traversal. Write/append input format: `"<path>|||<content>"`.

### `agent/tools/calculator.py` — Safe Calculator

`calculate(expression)` parses with `ast`, walks only whitelisted nodes (literals, arithmetic ops, comparisons, whitelisted math functions/constants), rejects attributes (except `math.*`), calls, imports, lambdas, and dunders.

### `agent/tools/security.py` — Security Toolkit

- `security_scan("tool|args")` — runs `nmap`/`sqlmap`/`gobuster`/`nikto` via `subprocess` (no shell), with timeout + `FileNotFoundError` handling. `sqlmap` is forced into `--batch` mode.
- `osint_lookup(target)` — Shodan (if API key set) or `ipinfo.io` fallback; resolves hostnames to IPs.
- `analyze_packets("interface|count")` — scapy capture + protocol/src/dst summary.
- `explain_vulnerability(type)` — structured educational write-ups for 7 vuln classes.

### `agent/memory.py` — Memory

`ConversationMemory` keeps the last N turns (default 20) plus a persistent system prompt. Supports `add_message`, `get_history`, `clear`, `save_to_file`, `load_from_file` (JSON).

### `agent/llm.py` — LLM Client

`LLMClient.chat(messages)` POSTs to Ollama's OpenAI-compatible endpoint using `requests`. On `ConnectionError` it prints a friendly "start `ollama serve`" message and exits. On 4xx/5xx it logs and raises `LLMHTTPError`. On timeout it raises `LLMTimeoutError`.

### `agent/logger.py` — Logging

Console (INFO) + rotating file (`logs/agent.log`, DEBUG, 5 MB × 3 backups). Logs all ReAct iterations, tool calls (truncated to 500 chars), LLM requests (with token usage if reported), and full tracebacks on errors.

---

## Testing

Two test suites are included. Neither requires a real LLM.

### Component tests (`smoke_test.py`)

Exercises config loading, the tool registry, the calculator (including security rejections), filesystem sandboxing (traversal + absolute path blocked), memory windowing + persistence, vulnerability explanations, the disclaimer, ReAct JSON parsing, and tool dispatch safety.

```bash
python smoke_test.py
# Expected: RESULT: ALL CHECKS PASSED ✓
```

### End-to-end ReAct loop test (`e2e_test.py`)

Starts a mock OpenAI-compatible server (`mock_ollama_server.py`) and runs the **full Plan→Act→Observe→Respond loop** with real tool execution (real web search, real file writes, real calculator evaluation) across multiple queries.

```bash
python e2e_test.py
# Expected: === N assertion(s) passed ===  (exit 0)
```

### Mock server (for manual experimentation)

```bash
python mock_ollama_server.py --port 11435
# then in config.yaml set llm.endpoint to http://localhost:11435/v1/chat/completions
```

---

## Troubleshooting

**"Could not connect to the Ollama server"**
→ Ollama isn't running. Start it with `ollama serve` in a separate terminal, then re-run the agent.

**HTTP 404 / "model not found"**
→ You haven't pulled the model. Run `ollama pull llama3.2` (or whichever model `config.yaml` specifies).

**`Error: 'nmap' is not installed`**
→ Install the OS package (see Step 4). The agent never crashes on a missing tool — it returns a descriptive message.

**`permission denied` on packet capture or nmap**
→ Live capture / certain nmap scans need root. Run with `sudo` or grant `CAP_NET_RAW`.

**DuckDuckGo returns "No results found" / rate-limited**
→ The tool retries automatically. If it persists, wait a minute (DuckDuckGo rate-limits aggressive use) or reduce `search.max_results`.

**`pip install` fails for scapy**
→ Install `libpcap-dev` (Linux) or `libpcap` (macOS) first.

**Memory not persisting between runs**
→ Ensure `memory.persistence_file` is set (not `null`) and the sandbox directory is writable.

---

## Ethical Use

This agent includes a cybersecurity toolkit. **Use it only on systems you own or have explicit written permission to test.** The system prompt instructs the LLM to:

- Assist with authorized security research, ethical pentesting, and education.
- Freely explain vulnerabilities and remediation (defensive knowledge).
- Ask for authorization confirmation before running offensive tools when intent is unclear.
- Refuse and clearly state when a request falls outside ethical boundaries.

The mandatory disclaimer is printed at every agent startup and prefixed to all security tool output. Unauthorized access to systems you do not own is illegal and unethical. The developer assumes no liability for misuse.
