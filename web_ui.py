import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ---------- API Keys (From Render Environment Variables) ----------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
FISH_API_KEY = os.environ.get("FISH_API_KEY")
JACK_SPARROW_VOICE_ID = os.environ.get("JACK_SPARROW_VOICE_ID")

def llm_chat(query):
    if not GROQ_API_KEY:
        return "GROQ_API_KEY not set. Please configure it in Render environment variables."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": query}]}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM Error: {e}"

# ---------- Web UI Template ----------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sparrow AI Agent</title>
    <style>
        body { font-family: sans-serif; background: #0d1117; color: #e6edf3; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { width: 100%; max-width: 600px; background: #161b22; border-radius: 20px; padding: 20px; box-shadow: 0 0 30px rgba(0,0,0,0.8); }
        .header { text-align: center; font-size: 24px; font-weight: bold; color: #ff7f0e; margin-bottom: 20px; }
        .chat-box { height: 400px; overflow-y: auto; background: #0d1117; border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 1px solid #30363d; }
        .msg { padding: 10px 15px; border-radius: 18px; margin-bottom: 10px; max-width: 80%; word-wrap: break-word; }
        .user { background: #1f6feb; color: white; align-self: flex-end; margin-left: auto; }
        .agent { background: #21262d; border: 1px solid #30363d; align-self: flex-start; }
        .input-area { display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 12px; border-radius: 30px; border: 1px solid #30363d; background: #0d1117; color: white; outline: none; }
        .input-area button { padding: 12px 25px; border-radius: 30px; border: none; background: #1f6feb; color: white; font-weight: bold; cursor: pointer; }
        .footer { text-align: center; font-size: 12px; color: #484f58; margin-top: 10px; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">🏴‍☠️ Sparrow AI</div>
    <div class="chat-box" id="chatBox">
        <div class="msg agent">Ahoy! Captain Jack Sparrow's AI at your service. Ask me anything.</div>
    </div>
    <div class="input-area">
        <input type="text" id="inputBox" placeholder="Type your message..." autofocus>
        <button id="sendBtn">Send</button>
    </div>
    <div class="footer">⚡ Powered by Groq LLM | Jack Sparrow Voice</div>
</div>
<script>
    const input = document.getElementById('inputBox');
    const sendBtn = document.getElementById('sendBtn');
    const chat = document.getElementById('chatBox');

    function addMessage(text, type) {
        const div = document.createElement('div');
        div.className = `msg ${type}`;
        div.textContent = text;
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    }

    async function sendMessage() {
        const msg = input.value.trim();
        if (!msg) return;
        addMessage(msg, 'user');
        input.value = '';
        input.disabled = true;
        sendBtn.disabled = true;

        try {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: msg })
            });
            const data = await res.json();
            addMessage(data.response, 'agent');
        } catch(e) {
            addMessage('Error: Could not reach server.', 'agent');
        }
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({'response': 'Empty query.'})
    try:
        response = llm_chat(query)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f"Error: {e}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
