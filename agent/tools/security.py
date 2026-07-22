import subprocess
import hashlib
import requests
import json

DISCLAIMER = "WARNING: Security tools are for authorized/educational use only."

def tool_shell(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Command timed out."
    except Exception as e:
        return f"Shell Error: {e}"

def tool_explain(vuln):
    vulns = {
        "sqli": "SQL Injection: Use parameterized queries.",
        "xss": "Cross-Site Scripting: Sanitize outputs.",
        "csrf": "CSRF: Use tokens.",
        "lfi": "Local File Inclusion: Whitelist paths.",
        "rce": "Remote Code Execution: Validate inputs."
    }
    return vulns.get(vuln.lower(), "Unknown vulnerability.")

def tool_nmap(target):
    if not target:
        return "Error: Provide target"
    try:
        result = subprocess.run(["nmap", "-sV", "-T4", target], capture_output=True, text=True, timeout=300)
        return f"NMAP RESULT:\n{result.stdout}\n{result.stderr}"
    except Exception as e:
        return f"Nmap Error: {e}"

def tool_whois(domain):
    if not domain:
        return "Error: Provide domain"
    try:
        result = subprocess.run(["whois", domain], capture_output=True, text=True, timeout=60)
        return f"WHOIS RESULT:\n{result.stdout}"
    except Exception as e:
        return f"WHOIS Error: {e}"

def tool_dns(domain):
    if not domain:
        return "Error: Provide domain"
    try:
        result = subprocess.run(["dig", domain], capture_output=True, text=True, timeout=60)
        return f"DNS RESULT:\n{result.stdout}"
    except Exception as e:
        return f"DNS Error: {e}"

def tool_subdomain_enum(domain):
    if not domain:
        return "Error: Provide domain"
    
    domain = domain.replace("https://", "").replace("http://", "").strip("/")
    
    try:
        # HackerTarget API for fast and reliable subdomain lookup
        url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
        resp = requests.get(url, timeout=15)
        
        if resp.status_code == 200 and "error" not in resp.text.lower():
            lines = resp.text.strip().split("\n")
            subdomains = [line.split(",")[0] for line in lines if "," in line]
            if subdomains:
                return f"Found {len(subdomains)} subdomains for {domain}:\n" + "\n".join(subdomains[:15])
        
        # Fallback to crt.sh if HackerTarget fails
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            subs = set([item['name_value'] for item in data if 'name_value' in item])
            clean_subs = [s for s in subs if not s.startswith('*')]
            if clean_subs:
                return f"Found subdomains for {domain}:\n" + "\n".join(list(clean_subs)[:15])

        return f"Could not fetch subdomains for {domain}."
    except Exception as e:
        return f"Subdomain Enum Error: {e}"

def tool_hash_crack(hash_value):
    if not hash_value:
        return "Error: Provide hash"
    wordlist = ["password", "123456", "123456789"]
    hash_type = "MD5" if len(hash_value) == 32 else "Unknown"
    for word in wordlist:
        if hash_type == "MD5" and hashlib.md5(word.encode()).hexdigest() == hash_value:
            return f"Cracked! [MD5] Word: {word}"
    return "Not found."

def tool_http_req(url):
    if not url:
        return "Error: Provide URL."
    try:
        headers = {'User-Agent': 'SuperNinja-Agent'}
        resp = requests.get(url, timeout=15, headers=headers)
        return f"HTTP {url}\nStatus: {resp.status_code}\nHeaders: {dict(resp.headers)}\nBody: {resp.text[:500]} ..."
    except Exception as e:
        return f"HTTP Error: {e}"
