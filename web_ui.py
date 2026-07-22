from flask import Flask, request, jsonify, render_template_string
from agent.core import ReActAgent
from agent.config_loader import load_config

app = Flask(__name__)
config = load_config("config.yaml")
agent = ReActAgent(config)
agent.set_logger(None)

HTML = """
<!DOCTYPE html>
<html>
<head><title>🤖 Super Agent</title>
<style>
body { background: #0d1117; color: #e6edf3; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin:0; }
.container { width: 100%; max-width: 600px; height: 90vh; background: #161b22; border-radius: 20px; display: flex; flex-direction: column; overflow: hidden; }
.header { background: #1f242f; padding: 15px; text-align: center; font-weight: bold; border-bottom: 1px solid #30363d; }
.messages { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
.msg { padding: 10px 15px; border-radius: 18px; max-width: 80%; word-wrap: break-word; }
.user { align-self: flex-end; background: #1f6feb; color: white; }
.agent { align-self: flex-start; background: #21262d; border: 1px solid #30363d; }
.input-area { display: flex; padding: 15px; gap: 10px; background: #0d1117; border-top: 1px solid #30363d; }
.input-area input { flex: 1; padding: 12px; border-radius: 30px; border: 1px solid #30363d; background: #0d1117; color: white; outline: none; }
.input-area button { padding: 12px 25px; border-radius: 30px; border: none; background: #1f6feb; color: white; font-weight: bold; cursor: pointer; }
</style>
</head>
<body>
<div class="container">
<div class="header">🤖 Super Hacker Agent</div>
<div class="messages" id="chatBox"><div class="msg agent">Ready. Try: nmap 127.0.0.1 | calc 2+2</div></div>
<div class="input-area"><input id="inp" placeholder="Ask..." autofocus><button id="btn">Send</button></div>
</div>
<script>
const inp = document.getElementById('inp'), btn = document.getElementById('btn'), chat = document.getElementById('chatBox');
function add(t, type){ const d=document.createElement('div'); d.className='msg '+type; d.textContent=t; chat.appendChild(d); chat.scrollTop=chat.scrollHeight; }
async function send(){ const q=inp.value.trim(); if(!q)return; add(q,'user'); inp.value=''; inp.disabled=true; btn.disabled=true;
try{ const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:q})}); const d=await r.json(); add(d.response,'agent'); }catch(e){ add('Error','agent'); }
inp.disabled=false; btn.disabled=false; inp.focus(); }
btn.onclick=send; inp.onkeypress=(e)=>e.key==='Enter'&&send();
</script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    try:
        res = agent.run(data.get('query', ''))
        return jsonify({'response': str(res)})
    except Exception as e:
        return jsonify({'response': f"Error: {e}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
