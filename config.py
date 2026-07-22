import os

LLM_PROVIDER = "ollama"
OLLAMA_ENDPOINT = "http://127.0.0.1:11434/v1/chat/completions"
OLLAMA_MODEL = "llama3.2:1b"

FISH_API_KEY = "2c048acd04a54aa5b176ebe366332649"
FISH_TTS_URL = "https://api.fish.audio/v1/tts"
JACK_SPARROW_VOICE_ID = "YOUR_VOICE_ID_HERE"  # <-- Fish Audio-ல Train பண்ணிட்டு இதை மாத்துங்க!

DEFAULT_TTS_LANG = "en"
SUPPORTED_LANGUAGES = ["en", "ta", "hi", "fr", "es", "de", "ja", "zh"]
DEFAULT_LANG = "en"
MAX_RETRIES = 3
AUTO_REBIRTH = True
