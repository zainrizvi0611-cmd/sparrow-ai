import requests

class Translator:
    def __init__(self, config):
        self.supported_langs = config.SUPPORTED_LANGUAGES
    
    def translate(self, text, target_lang):
        if target_lang == "en":
            return text
        try:
            response = requests.post(
                "https://libretranslate.com/translate",
                json={"q": text, "source": "en", "target": target_lang, "format": "text"},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()["translatedText"]
            return text
        except:
            return text
    
    def detect_language(self, text):
        try:
            response = requests.post(
                "https://libretranslate.com/detect",
                json={"q": text},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()[0]["language"]
            return "en"
        except:
            return "en"
