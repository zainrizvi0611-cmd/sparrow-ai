import json
from datetime import datetime

class Memory:
    def __init__(self, window_turns=10):
        self.window_turns = window_turns
        # Ensure history is ALWAYS a list
        self.history = [{"role": "system", "content": "You are a helpful AI assistant with tools."}]
    
    def add_message(self, role, content):
        # Ensure history is a list before appending
        if not isinstance(self.history, list):
            self.history = [{"role": "system", "content": "You are a helpful AI assistant with tools."}]
        self.history.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        # Sliding window
        user_turns = [m for m in self.history if m.get("role") == "user"]
        if len(user_turns) > self.window_turns:
            # Keep system + last window_turns*2 messages
            self.history = [self.history[0]] + self.history[-(self.window_turns*2):]
    
    def get_history(self):
        # Ensure we always return a list
        if not isinstance(self.history, list):
            self.history = [{"role": "system", "content": "You are a helpful AI assistant with tools."}]
        return self.history
    
    def clear(self):
        self.history = [{"role": "system", "content": "You are a helpful AI assistant with tools."}]
    
    def save_to_file(self, path):
        # Always save as a list
        if not isinstance(self.history, list):
            self.history = [{"role": "system", "content": "You are a helpful AI assistant with tools."}]
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2)
    
    def load_from_file(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.history = data
                    return True
                else:
                    # If corrupted, reset
                    self.clear()
                    return False
        except:
            self.clear()
            return False
