import logging
import json
from src.utils.dcs_bios import DcsBiosSender
from src.utils.input_emitter import InputEmitter
from src.profiles import oh58d

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Bridge:
    def __init__(self):
        self.sender = DcsBiosSender()
        self.keyboard = InputEmitter()
        self.profiles = {
            "OH-58D": oh58d
            # Add AH-64D later
        }

    def process_intent(self, intent_json):
        """
        Parses the intent JSON and executes the command.
        
        Expected JSON structure:
        {
          "aircraft": "OH-58D",
          "action": "search_sector",
          "parameters": { ... }
        }
        """
        try:
            # If input is a string, parse it. If dict, use as is.
            # If input is a string, parse it. If dict/list, use as is.
            if isinstance(intent_json, str):
                data = json.loads(intent_json)
            else:
                data = intent_json

            # Handle List output (rare LLM flake) - take the first item
            if isinstance(data, list):
                if len(data) > 0:
                    logging.warning("Received a list of intents. Using the first one.")
                    data = data[0]
                else:
                    logging.error("Received empty list of intents.")
                    return False

            if not isinstance(data, dict):
                logging.error(f"Invalid intent format. Expected dict, got {type(data)}")
                return False

            aircraft = data.get("aircraft")
            action = data.get("action")
            parameters = data.get("parameters", {})

            if not aircraft or not action:
                logging.error("Invalid intent: missing aircraft or action")
                return False

            profile = self.profiles.get(aircraft)
            if not profile:
                logging.error(f"Profile not found for aircraft: {aircraft}")
                return False

            command = profile.get_command(action, parameters)
            if command:
                # Check if it's a specialized command dict or a simple string
                if isinstance(command, dict) and command.get("type") == "keyboard":
                    keys = command.get("keys")
                    logging.info(f"Executing Keyboard Combo: {keys} for {aircraft}")
                    self.keyboard.press_combo(keys)
                elif isinstance(command, str):
                    logging.info(f"Executing BIOS: {command} for {aircraft}")
                    self.sender.send_command(command)
                return True
            else:
                logging.warning(f"No command mapping found for action: {action}")
                return False

        except json.JSONDecodeError:
            logging.error("Failed to decode JSON intent")
            return False
        except Exception as e:
            logging.error(f"Error processing intent: {e}")
            return False

    def close(self):
        self.sender.close()
