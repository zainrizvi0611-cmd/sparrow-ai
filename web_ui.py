import os
import requests
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from authlib.integrations.flask_client import OAuth
from flask_session import Session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "SparrowAI@2026")

# ---------- Session Config ----------
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ---------- OAuth Setup ----------
oauth = OAuth(app)

# Google OAuth
google = oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# ---------- Groq LLM ----------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def llm_chat(query):
    if not GROQ_API_KEY:
        return "GROQ_API_KEY not set."
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": query}],
        "temperature": 0.7
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()
        if response.status_code == 200:
            return data["choices"][0]["message"]["content"]
        else:
            return f"API Error: {data.get('error', {}).get('message', 'Unknown error')}"
    except Exception as e:
        return f"LLM Error: {e}"

# ---------- Web UI Template ----------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sparrow AI Agent</title>
    <style>
        body { font-family: sans-serif; background: #0d1117; color: #e6edf3; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .container { width: 100%; max-width: 600px; background: #161b22; border-radius: 20px; padding: 20px; box-shadow: 0 0 30px rgba(0,0,0,0.8); }
        .header { text-align: center; font-size: 24px; font-weight: bold; color: #ff7f0e; margin-bottom: 10px; }
        .sub-header { text-align: center; font-size: 14px; color: #8b949e; margin-bottom: 20px; }
        .sub-header a { color: #ff7f0e; text-decoration: none; }
        .chat-box { height: 400px; overflow-y: auto; background: #0d1117; border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 1px solid #30363d; }
        .msg { padding: 10px 15px; border-radius: 18px; margin-bottom: 10px; max-width: 80%; word-wrap: break-word; }
        .user { background: #1f6feb; color: white; align-self: flex-end; margin-left: auto; }
        .agent { background: #21262d; border: 1px solid #30363d; align-self: flex-start; }
        .input-area { display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 12px; border-radius: 30px; border: 1px solid #30363d; background: #0d1117; color: white; outline: none; }
        .input-area button { padding: 12px 25px; border-radius: 30px; border: none; background: #1f6feb; color: white; font-weight: bold; cursor: pointer; }
        .footer { text-align: center; font-size: 12px; color: #484f58; margin-top: 10px; }
        .login-area { text-align: center; margin-bottom: 15px; }
        .login-area a { display: inline-block; margin: 5px 10px; padding: 10px 20px; background: #21262d; border: 1px solid #30363d; border-radius: 30px; color: #e6edf3; text-decoration: none; }
        .login-area a:hover { background: #30363d; }
        .profile { text-align: center; font-size: 14px; color: #8b949e; margin-bottom: 15px; }
        .profile img { width: 40px; height: 40px; border-radius: 50%; vertical-align: middle; margin-right: 10px; }
        .profile a { color: #ff7f0e; text-decoration: none; }
        .btn-logout { background: #21262d; border: 1px solid #30363d; color: #e6edf3; padding: 8px 16px; border-radius: 30px; cursor: pointer; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">🏴‍☠️ Sparrow AI</div>
    <div class="sub-header">Created by <a href="https://instagram.com/zainrizvi0611" target="_blank">@zainrizvi0611</a></div>

    <!-- Login / Profile Area -->
    <div class="login-area">
        {% if session.user %}
            <div class="profile">
                <img src="{{ session.user.avatar }}" alt="Avatar">
                <strong>{{ session.user.name }}</strong> ({{ session.user.email }})
                <a href="/logout" class="btn-logout">Logout</a>
            </div>
        {% else %}
            <a href="/login/google">🔑 Google Login</a>
        {% endif %}
    </div>

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

# ---------- Routes ----------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    # Require login to chat
    if not session.get('user'):
        return jsonify({'response': 'Please login first.'})
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({'response': 'Empty query.'})
    try:
        response = llm_chat(query)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f"Error: {e}"})

# ---------- Google Login ----------
@app.route('/login/google')
def login_google():
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/google')
def authorize_google():
    token = google.authorize_access_token()
    user_info = google.parse_id_token(token)
    session['user'] = {
        'name': user_info.get('name'),
        'email': user_info.get('email'),
        'avatar': user_info.get('picture'),
        'provider': 'Google'
    }
    return redirect('/')

# ---------- Logout ----------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
