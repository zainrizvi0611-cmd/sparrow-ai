import json
from pathlib import Path

SANDBOX = Path("./agent_workspace")
SANDBOX.mkdir(exist_ok=True)

def _safe_path(filename):
    p = SANDBOX / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def read_file(filename):
    """Read a file from the sandbox."""
    p = _safe_path(filename)
    if not p.exists():
        return f"File '{filename}' not found."
    return p.read_text()

def write_file(input_data):
    """Write content to a file. Handles both string and dict input."""
    if isinstance(input_data, dict):
        filename = input_data.get("filename") or input_data.get("file") or input_data.get("path")
        content = input_data.get("content") or input_data.get("data") or input_data.get("text")
        if not filename or content is None:
            return "Error: write_file requires 'filename' and 'content' keys."
        p = _safe_path(filename)
        p.write_text(str(content))
        return f"Written to {filename}"

    if isinstance(input_data, str):
        # Try format: "filename with content Hello"
        if " with content " in input_data:
            parts = input_data.split(" with content ", 1)
            filename = parts[0].strip()
            content = parts[1].strip()
            if filename and content:
                p = _safe_path(filename)
                p.write_text(content)
                return f"Written to {filename}"
        # Try JSON string
        try:
            data = json.loads(input_data)
            if isinstance(data, dict):
                return write_file(data)
        except:
            pass
        return f"Error: Could not parse input. Expected format: 'filename with content Your text' or JSON."
    return "Error: Invalid input type."

def append_file(input_data):
    """Append content to a file. Handles both string and dict input."""
    if isinstance(input_data, dict):
        filename = input_data.get("filename") or input_data.get("file")
        content = input_data.get("content") or input_data.get("data")
        if not filename or content is None:
            return "Error: append_file requires 'filename' and 'content' keys."
        p = _safe_path(filename)
        with open(p, "a") as f:
            f.write(str(content) + "\n")
        return f"Appended to {filename}"

    if isinstance(input_data, str):
        if " with content " in input_data:
            parts = input_data.split(" with content ", 1)
            filename = parts[0].strip()
            content = parts[1].strip()
            if filename and content:
                p = _safe_path(filename)
                with open(p, "a") as f:
                    f.write(content + "\n")
                return f"Appended to {filename}"
        try:
            data = json.loads(input_data)
            if isinstance(data, dict):
                return append_file(data)
        except:
            pass
        return f"Error: Could not parse input. Expected format: 'filename with content Your text'."
    return "Error: Invalid input type."
