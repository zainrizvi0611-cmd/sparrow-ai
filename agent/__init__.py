"""
agent
====

Top-level package for the Autonomous ReAct AI Agent.

Sub-packages / modules:
    agent.config_loader  — loads and validates config.yaml
    agent.logger         — structured rotating logging
    agent.memory         — sliding-window conversation buffer
    agent.llm            — Ollama (OpenAI-compatible) client
    agent.core           — the ReAct Plan→Act→Observe→Respond loop
    agent.tools          — tool implementations (search, fs, calc, security)
"""

__version__ = "1.0.0"
__author__ = "SuperNinja AI Architect"
