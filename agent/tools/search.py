"""
agent.tools.search
==================

Web search tool backed by the ``duckduckgo_search`` library (the maintained
``DDGS`` client). Exposes a single function ``web_search(query) -> str`` that
returns the top results formatted as plain text.

Behaviour
---------
- Returns the top ``max_results`` hits (default 5), each formatted as:
      [1] Title
          URL
          Snippet
- Implements a bounded retry loop for transient / rate-limit errors:
  up to ``max_retries`` extra attempts with ``retry_delay`` seconds between.
- NEVER raises: on failure it returns a descriptive error string so the ReAct
  loop can present it to the LLM as an observation.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from ..logger import get_logger

_log = get_logger()

# Module-level configuration defaults. The agent core injects values from
# config.yaml via ``configure_search`` at startup, but these defaults make the
# tool usable in isolation (e.g. in unit tests).
_MAX_RESULTS: int = 5
_MAX_RETRIES: int = 2
_RETRY_DELAY: float = 2.0


def configure_search(max_results: int, max_retries: int, retry_delay: float) -> None:
    """
    Override module defaults from config. Called once at agent startup.
    """
    global _MAX_RESULTS, _MAX_RETRIES, _RETRY_DELAY
    _MAX_RESULTS = max(1, int(max_results))
    _MAX_RETRIES = max(0, int(max_retries))
    _RETRY_DELAY = max(0.0, float(retry_delay))
    _log.debug(
        "search configured: max_results=%d max_retries=%d retry_delay=%.1fs",
        _MAX_RESULTS,
        _MAX_RETRIES,
        _RETRY_DELAY,
    )


def _format_results(results: list) -> str:
    """
    Turn a list of result dicts (each with title/href/body) into a readable
    numbered text block.
    """
    if not results:
        return "No results found for the query."
    lines = []
    for idx, item in enumerate(results, start=1):
        title = item.get("title") or "(no title)"
        url = item.get("href") or item.get("url") or "(no url)"
        snippet = item.get("body") or item.get("snippet") or ""
        lines.append(f"[{idx}] {title}")
        lines.append(f"    URL: {url}")
        if snippet:
            # Keep snippets to a reasonable length for the LLM context window.
            snippet = snippet.replace("\n", " ").strip()
            if len(snippet) > 300:
                snippet = snippet[:300] + "..."
            lines.append(f"    {snippet}")
        lines.append("")  # blank line between entries
    return "\n".join(lines).strip()


def web_search(query: str) -> str:
    """
    Perform a DuckDuckGo web search and return formatted results.

    Parameters
    ----------
    query:
        The search query string.

    Returns
    -------
    str
        Formatted results, or an error message. Never raises.
    """
    query = (query or "").strip()
    if not query:
        return "Error: empty search query."

    # Import lazily so the module can be imported even if the package isn't
    # installed yet (e.g. during partial setup). The error is surfaced as a
    # tool observation rather than a crash.
    #
    # The DuckDuckGo search library was renamed: ``duckduckgo_search`` is the
    # legacy name (now deprecated/empty), ``ddgs`` is the current package.
    # We try the new package first, then fall back to the legacy one so the
    # tool works regardless of which the user installed.
    DDGS = None
    try:
        from ddgs import DDGS  # type: ignore  # current package name
    except ImportError:
        try:
            from duckduckgo_search import DDGS  # type: ignore  # legacy name
        except ImportError as exc:
            msg = (
                "Error: no DuckDuckGo search library is installed. "
                "Run: pip install ddgs   (recommended) "
                "or: pip install duckduckgo-search"
            )
            _log.error(msg + " (%s)", exc)
            return msg

    attempt = 0
    last_error: Optional[str] = None
    # Total attempts = 1 initial + max_retries.
    while attempt <= _MAX_RETRIES:
        try:
            _log.info("web_search attempt %d: '%s'", attempt + 1, query)
            # ``DDGS().text`` returns dicts with keys: title, href, body.
            # The new ``ddgs`` package supports both a context manager and direct
            # instantiation; we guard both so the tool works across versions.
            try:
                ddgs_ctx = DDGS()
                raw_results: Any = ddgs_ctx.text(query, max_results=_MAX_RESULTS)
                results = list(raw_results) if raw_results else []
                # Close if a close method exists (context-manager variants).
                if hasattr(ddgs_ctx, "close"):
                    try:
                        ddgs_ctx.close()
                    except Exception:
                        pass
            except TypeError:
                # Fallback: some versions want the query as a positional arg
                # or use a different keyword; retry with positional form.
                ddgs_ctx = DDGS()
                raw_results = ddgs_ctx.text(query, _MAX_RESULTS)  # type: ignore[call-arg]
                results = list(raw_results) if raw_results else []
                if hasattr(ddgs_ctx, "close"):
                    try:
                        ddgs_ctx.close()
                    except Exception:
                        pass
            formatted = _format_results(results)
            _log.info("web_search success: %d results", len(results))
            return formatted
        except Exception as exc:  # broad catch is intentional for a tool
            last_error = f"{type(exc).__name__}: {exc}"
            _log.warning("web_search attempt %d failed: %s", attempt + 1, last_error)
            # DuckDuckGo frequently rate-limits; a short sleep often resolves it.
            if attempt < _MAX_RETRIES:
                time.sleep(_RETRY_DELAY)
            attempt += 1

    return (
        f"Error: web search failed after {attempt} attempt(s). Last error: {last_error}. "
        "DuckDuckGo may be rate-limiting requests; try again later."
    )
