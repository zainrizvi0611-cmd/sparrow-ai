import subprocess
import tempfile
import os
import re
from gtts import gTTS
from god_mode_final import NoRefusalGod

agent = NoRefusalGod()
DEFAULT_LANG = "ta"

def speak(text, lang=DEFAULT_LANG):
    clean_text = re.sub(r'[^\w\s.,!?]', '', text)[:500]
    print(f"🤖 Agent: {clean_text}")
    
    # Try gTTS + mpg123 (Best)
    try:
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            # Try mpg123 (ALSA/Pulse compatible)
            subprocess.run(["mpg123", "-q", fp.name], check=False, timeout=10)
            os.unlink(fp.name)
            return
    except Exception as e:
        print(f"⚠️ mpg123 Error: {e}")
    
    # Fallback: espeak-ng (Robotic)
    try:
        subprocess.run(["espeak-ng", "-v", f"{lang}+f3", clean_text], check=False)
    except:
        pass

if __name__ == "__main__":
    print("🎤 Voice Keyboard Mode Active. Type your query.")
    while True:
        query = input("⌨️ You> ").strip()
        if not query:
            continue
        if query.lower() in ["exit", "quit", "bye", "பை"]:
            speak("Goodbye!")
            break
        response = agent.run(query)
        speak(response)
