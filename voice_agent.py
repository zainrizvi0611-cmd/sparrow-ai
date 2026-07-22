import speech_recognition as sr
import subprocess
import re
from god_mode_final import NoRefusalGod

agent = NoRefusalGod()
r = sr.Recognizer()

def speak(text):
    # Remove special characters and limit length
    clean_text = re.sub(r'[^\w\s.,!?]', '', text)[:500]
    print(f"🤖 Agent: {clean_text}")
    # Use espeak-ng directly (no pygame)
    subprocess.run(["espeak-ng", "-v", "ta", clean_text], check=False)

def listen():
    with sr.Microphone() as source:
        print("🎤 Listening... (Speak now)")
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(audio, language='ta-IN')
            print(f"👤 You said: {text}")
            return text
        except sr.WaitTimeoutError:
            print("⏰ No speech detected.")
            return None
        except sr.UnknownValueError:
            print("🤔 Could not understand.")
            return None
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return None

if __name__ == "__main__":
    speak("Voice Agent Activated! Ask me anything.")
    while True:
        query = listen()
        if query:
            if query.lower() in ["exit", "quit", "bye"]:
                speak("Goodbye!")
                break
            response = agent.run(query)
            speak(response)
