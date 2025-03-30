import os
import json

def load_config(config_path):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"❌ Config file '{config_path}' not found.")

        with open(config_path, "r") as f:
            return json.load(f)   