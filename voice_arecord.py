import subprocess
import tempfile
import os
import re
import speech_recognition as sr
from gtts import gTTS
from god_mode_final import NoRefusalGod

agent = NoRefusalGod()
DEFAULT_LANG = "ta"
WAKE_WORDS = ["hey sparrow", "sparrow", "ஏய் ஸ்பேரோ"]

def speak(text, lang=DEFAULT_LANG):
    clean_text = re.sub(r'[^\w\s.,!?]', '', text)[:500]
    print(f"🤖 Agent: {clean_text}")
    try:
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", fp.name], check=False)
            os.unlink(fp.name)
    except:
        subprocess.run(["espeak-ng", "-v", f"{lang}+f3", clean_text], check=False)

def listen_for_wake():
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        filename = tmp.name
    print("🎤 [Listening for Wake Word: 'Hey Ninja' or 'Jarvis']...")
    subprocess.run(["arecord", "-f", "cd", "-t", "wav", "-d", "5", filename], check=False)
    try:
        r = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language='ta-IN').lower()
        print(f"👤 Heard: {text}")
        for word in WAKE_WORDS:
            if word in text:
                return True
        return False
    except:
        return False
    finally:
        os.unlink(filename)

def listen_command():
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        filename = tmp.name
    print("🎤 Recording Command... (Speak now)")
    subprocess.run(["arecord", "-f", "cd", "-t", "wav", "-d", "5", filename], check=False)
    try:
        r = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language='ta-IN')
        print(f"👤 You: {text}")
        return text
    except:
        return None
    finally:
        os.unlink(filename)

if __name__ == "__main__":
    speak("Jarvis Mode Active. Say 'Hey Ninja' to wake me up.")
    while True:
        if listen_for_wake():
            speak("Yes sir, how can I help?")
            query = listen_command()
            if query:
                if "exit" in query.lower() or "bye" in query.lower():
                    speak("Goodbye sir!")
                    break
                response = agent.run(query)
                speak(response)
