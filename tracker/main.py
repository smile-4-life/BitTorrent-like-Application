import sys
import os

# Ensure the parent directory (project root) is in the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shared.config_loader import load_config

CONFIG_PATH = "config/tracker_config.json"
config = load_config(CONFIG_PATH)

def start_tracker():
    print(f"[Tracker] Loaded config: {config}")
    print("[Tracker] Running...")

if __name__ == "__main__":
    start_tracker()
