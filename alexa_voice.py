import speech_recognition as sr
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
    print(f"🤖 Agent ({lang}): {clean_text}")
    try:
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", fp.name],
                check=False
            )
            os.unlink(fp.name)
    except Exception as e:
        print(f"⚠️ TTS Error: {e}. Fallback to espeak-ng.")
        subprocess.run(["espeak-ng", "-v", f"{lang}+f3", clean_text], check=False)

def listen():
    # Try to use microphone
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening... (Speak now)")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(audio, language='ta-IN')
            print(f"👤 You (Tamil): {text}")
            return text
    except Exception as e:
        print(f"⚠️ Microphone error: {e}")
        print("⌨️  Switching to keyboard input. Type your query:")
        return input("You> ")

if __name__ == "__main__":
    speak("Voice Agent Activated! (Fallback: keyboard if mic fails)", lang='ta')
    while True:
        query = listen()
        if query:
            if query.lower() in ["exit", "quit", "bye", "பை"]:
                speak("Goodbye!", lang='ta')
                break
            response = agent.run(query)
            speak(response, lang='ta')
