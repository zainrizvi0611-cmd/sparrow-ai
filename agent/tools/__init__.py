from agent.tools.filesystem import read_file, write_file, append_file
from agent.tools.calculator import calculator
from agent.tools.search import web_search
from agent.tools.security import (
    DISCLAIMER, tool_shell, tool_explain, 
    tool_nmap, tool_whois, tool_dns, tool_hash_crack, tool_http_req
)
from agent.tools.fraud import tool_predict_fraud

TOOL_REGISTRY = {
    "read_file": read_file,
    "write_file": write_file,
    "append_file": append_file,
    "calculator": calculator,
    "web_search": web_search,
    "shell": tool_shell,
    "explain_vulnerability": tool_explain,
    "nmap": tool_nmap,
    "whois": tool_whois,
    "dns": tool_dns,
    "hash_crack": tool_hash_crack,
    "http_req": tool_http_req,
    "predict_fraud": tool_predict_fraud,
}
