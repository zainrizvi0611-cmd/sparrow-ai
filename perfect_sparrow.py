import subprocess
import tempfile
import os
import re
import time
import speech_recognition as sr
from gtts import gTTS
from god_mode_final import NoRefusalGod

agent = NoRefusalGod()

# Termux Native Binaries (Absolute Paths from base system)
TERMUX_BIN = "/data/data/com.termux/files/usr/bin/"
MIC_RECORD = TERMUX_BIN + "termux-microphone-record"
MEDIA_PLAY = TERMUX_BIN + "termux-media-player"

def speak(text, lang='ta'):
    clean_text = re.sub(r'[^\w\s.,!?]', '', text)[:500]
    print(f"🦅 Sparrow: {clean_text}")
    try:
        tts = gTTS(text=clean_text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            audio_path = fp.name
            tts.save(audio_path)
            # Play using termux-media-player with the actual file path
            subprocess.run([MEDIA_PLAY, "play", audio_path], check=False, timeout=15)
            os.unlink(audio_path)
    except Exception as e:
        print(f"⚠️ Speak Error: {e}")

def listen():
    audio_file = "/tmp/sparrow_audio.wav"
    print("🎤 Listening... (Speak for 5 seconds)")
    try:
        subprocess.run([MIC_RECORD, "-f", audio_file, "-d", "5"], check=True, timeout=6)
    except Exception as e:
        print(f"⚠️ Record Error: {e}. Switching to Keyboard.")
        return input("⌨️ You> ")
    time.sleep(0.5)
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language='ta-IN')
        print(f"👤 You: {text}")
        os.remove(audio_file)
        return text
    except Exception as e:
        print(f"⚠️ STT Error: {e}")
        os.remove(audio_file)
        return input("⌨️ You> ")

if __name__ == "__main__":
    speak("Perfect Sparrow & Jarvis Combo Activated. Talk to me.")
    while True:
        query = listen()
        if query:
            if query.lower() in ["exit", "quit", "bye", "பை"]:
                speak("Goodbye sir!")
                break
            response = agent.run(query)
            speak(response)
