import config
from llm_manager import LLMManager
from voice_manager import VoiceManager
from translator import Translator
from self_healer import SelfHealer
from rebirth_manager import RebirthManager
from god_mode_final import NoRefusalGod

class SuperAgent:
    def __init__(self):
        self.config = config
        self.llm = LLMManager(config)
        self.voice = VoiceManager(config)
        self.translator = Translator(config)
        self.healer = SelfHealer()
        self.brain = NoRefusalGod()
        rebirth = RebirthManager()
        rebirth.auto_restart_on_crash()
    
    def run(self):
        self.voice.speak("Super Sparrow AI Activated. Multi-language, Self-Healing, Jack Sparrow Voice.")
        while True:
            query = self.voice.listen()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "bye"]:
                self.voice.speak("Goodbye sir!")
                break
            detected_lang = self.translator.detect_language(query)
            if detected_lang != "en":
                query_eng = self.translator.translate(query, "en")
            else:
                query_eng = query
            response = self.healer.wrap_function(self.brain.run, query_eng)
            if detected_lang != "en":
                response = self.translator.translate(response, detected_lang)
            self.voice.speak(response, voice_clone=True)
