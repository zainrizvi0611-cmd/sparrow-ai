import subprocess
import tempfile
import os
import re
import time
import speech_recognition as sr
from gtts import gTTS
import requests

class VoiceManager:
    def __init__(self, config):
        self.fish_api_key = config.FISH_API_KEY
        self.fish_tts_url = config.FISH_TTS_URL
        self.voice_id = config.JACK_SPARROW_VOICE_ID
        self.default_lang = config.DEFAULT_TTS_LANG
    
    def listen(self, lang='en-IN'):
        audio_file = "/tmp/sparrow_audio.wav"
        print("🎤 Listening... (Speak now)")
        try:
            subprocess.run(["termux-microphone-record", "-f", audio_file, "-d", "5"], check=True, timeout=10)
        except:
            return input("⌨️ You> ")
        time.sleep(0.5)
        try:
            r = sr.Recognizer()
            with sr.AudioFile(audio_file) as source:
                audio = r.record(source)
            text = r.recognize_google(audio, language=lang)
            print(f"👤 You: {text}")
            os.remove(audio_file)
            return text
        except:
            os.remove(audio_file)
            return input("⌨️ You> ")
    
    def speak(self, text, lang=None, voice_clone=True):
        if lang is None:
            lang = self.default_lang
        clean_text = re.sub(r'[^\w\s.,!?]', '', text)[:500]
        print(f"🗣️ AI: {clean_text}")
        
        if voice_clone and self.voice_id and self.voice_id != "YOUR_VOICE_ID_HERE":
            try:
                return self._fish_tts(clean_text)
            except Exception as e:
                print(f"⚠️ Fish TTS failed: {e}")
        
        try:
            return self._gtts_tts(clean_text, lang)
        except:
            pass
        
        try:
            subprocess.run(["termux-tts-speak", "-l", lang, clean_text], check=True, timeout=10)
        except:
            print("❌ No TTS available.")
    
    def _fish_tts(self, text):
        headers = {"Authorization": f"Bearer {self.fish_api_key}", "Content-Type": "application/json"}
        payload = {"text": text, "reference_id": self.voice_id, "format": "mp3"}
        response = requests.post(self.fish_tts_url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                fp.write(response.content)
                mp3_path = fp.name
            subprocess.run(["mpg123", "-q", mp3_path], check=True, timeout=20)
            os.unlink(mp3_path)
            return True
        raise Exception("Fish TTS failed")
    
    def _gtts_tts(self, text, lang):
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            mp3_path = fp.name
            tts.save(mp3_path)
        subprocess.run(["mpg123", "-q", mp3_path], check=True, timeout=20)
        os.unlink(mp3_path)
        return True
