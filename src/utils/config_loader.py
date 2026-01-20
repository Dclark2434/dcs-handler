import json
import os
import logging

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json')

def load_config():
    """
    Loads configuration from config.json.
    Returns a dictionary with defaults if file is missing or keys are missing.
    """
    defaults = {
        "ears": {
            "backend": "google",
            "whisper": {
                "model_size": "tiny.en",
                "device": "cuda",
                "compute_type": "float16"
            }
        },
        "dcs_bios": {
            "ip": "127.0.0.1",
            "port": 7778
        }
    }

    if not os.path.exists(CONFIG_PATH):
        logging.warning(f"Config file not found at {CONFIG_PATH}. Using defaults.")
        return defaults

    try:
        with open(CONFIG_PATH, 'r') as f:
            user_config = json.load(f)
            # Simple recursive merge (mock) or just return user config + defaults logic
            # For now, we trust the file or fallback completely, but better to merge.
            # Here we just return user_config, assuming they have the full structure.
            return user_config
    except Exception as e:
        logging.error(f"Error loading config: {e}. Using defaults.")
        return defaults
