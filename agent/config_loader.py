"""
agent.config_loader
===================

Loads ``config.yaml`` from disk, applies sane defaults for any missing keys,
and returns a validated, dot-accessible configuration object.

A lightweight ``Config`` class (a dict subclass with attribute access) is used
so modules can write ``config.llm.model`` instead of ``config['llm']['model']``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml


class Config(dict):
    """
    A dict subclass that allows attribute-style access to nested dictionaries.

    Example:
        cfg = Config({"llm": {"model": "llama3.2"}})
        cfg.llm.model  -> "llama3.2"
    """

    # __getattr__ is only called when normal attribute lookup fails, so it
    # won't shadow real dict methods (get, items, keys, etc.).
    def __getattr__(self, name: str) -> Any:
        try:
            value = self[name]
        except KeyError as exc:
            raise AttributeError(f"Config has no key '{name}'") from exc
        # Recursively wrap nested dicts so dot-access works at every level.
        if isinstance(value, dict) and not isinstance(value, Config):
            return Config(value)
        return value

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


# Default configuration — used to fill gaps if config.yaml is missing keys.
DEFAULTS: Dict[str, Any] = {
    "llm": {
        "endpoint": "http://localhost:11434/v1/chat/completions",
        "model": "llama3.2",
        "temperature": 0.7,
        "max_tokens": None,
        "timeout": 120,
        "top_p": 0.9,
    },
    "agent": {
        "max_iterations": 10,
    },
    "memory": {
        "window_turns": 20,
        "persistence_file": "agent_workspace/session_memory.json",
    },
    "filesystem": {
        "sandbox_dir": "agent_workspace",
    },
    "search": {
        "max_results": 5,
        "max_retries": 2,
        "retry_delay": 2,
    },
    "security": {
        "subprocess_timeout": 60,
        "shodan_api_key": None,
        "default_packet_count": 20,
    },
    "logging": {
        "log_dir": "logs",
        "console_level": "INFO",
        "file_level": "DEBUG",
        "max_bytes": 5 * 1024 * 1024,
        "backup_count": 3,
        "filename": "agent.log",
        "log_truncate_chars": 500,
    },
    "system_prompt": "",
}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge ``override`` into ``base``. Nested dicts are merged
    key-by-key; non-dict values in ``override`` replace those in ``base``.
    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(config_path: str | os.PathLike = "config.yaml") -> Config:
    """
    Load and validate the YAML configuration file.

    Parameters
    ----------
    config_path:
        Path to ``config.yaml`` (relative to CWD or absolute).

    Returns
    -------
    Config
        A dot-accessible config object with defaults applied.

    Raises
    ------
    FileNotFoundError
        If ``config_path`` does not exist.
    yaml.YAMLError
        If the YAML is malformed.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {path.resolve()}. "
            "Create a config.yaml (see the project README) or pass --config."
        )

    with path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    # Merge user config over defaults so missing keys are filled automatically.
    merged = _deep_merge(DEFAULTS, raw)

    # Basic validation of critical fields.
    llm = merged.get("llm", {})
    if not llm.get("endpoint"):
        raise ValueError("config.llm.endpoint must be a non-empty URL.")
    if not llm.get("model"):
        raise ValueError("config.llm.model must be specified (e.g. 'llama3.2').")

    max_iter = int(merged.get("agent", {}).get("max_iterations", 10))
    if max_iter < 1:
        raise ValueError("config.agent.max_iterations must be >= 1.")

    return Config(merged)
