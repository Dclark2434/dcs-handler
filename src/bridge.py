import logging
import json
from src.utils.dcs_bios import DcsBiosSender
from src.profiles import oh58d

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Bridge:
    def __init__(self):
        self.sender = DcsBiosSender()
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
            if isinstance(intent_json, str):
                data = json.loads(intent_json)
            else:
                data = intent_json

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
                logging.info(f"Executing: {command} for {aircraft}")
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
