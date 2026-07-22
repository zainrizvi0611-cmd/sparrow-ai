import os
import sys
import subprocess
import time

class RebirthManager:
    def __init__(self, script_path="main.py"):
        self.script_path = script_path
    
    def run_with_rebirth(self):
        while True:
            print("🦅 Sparrow AI Started. Monitoring for rebirth...")
            try:
                subprocess.run([sys.executable, self.script_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Agent crashed with exit code: {e.returncode}")
                print("♻️ Rebirth in 5 seconds...")
                time.sleep(5)
                continue
            except KeyboardInterrupt:
                print("👋 User stopped. Exiting.")
                break
            break
    
    def auto_restart_on_crash(self):
        import threading
        def monitor():
            while True:
                time.sleep(10)
                result = subprocess.run(["pgrep", "-f", "python.*main.py"], capture_output=True)
                if not result.stdout:
                    print("♻️ Agent died. Auto-rebirthing...")
                    subprocess.Popen(["python", "main.py"])
        threading.Thread(target=monitor, daemon=True).start()
