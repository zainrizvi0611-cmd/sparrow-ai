import subprocess
import traceback
import time

class SelfHealer:
    def __init__(self):
        self.error_log = []
    
    def wrap_function(self, func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = traceback.format_exc()
            self.error_log.append(error_msg)
            print(f"⚠️ Error Detected: {e}")
            return self._fix_and_retry(func, args, kwargs, e)
    
    def _fix_and_retry(self, func, args, kwargs, error):
        if "Connection refused" in str(error):
            print("🔄 Restarting Ollama...")
            subprocess.run(["pkill", "ollama"], check=False)
            subprocess.Popen(["nohup", "ollama", "serve", ">", "ollama.log", "2>&1", "&"])
            time.sleep(3)
            try:
                return func(*args, **kwargs)
            except:
                pass
        if "MemoryError" in str(error):
            print("🧹 Clearing memory...")
            import gc
            gc.collect()
            try:
                return func(*args, **kwargs)
            except:
                pass
        return "I encountered an error. Please try again."
