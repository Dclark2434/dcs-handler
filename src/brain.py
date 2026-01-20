import google.generativeai as genai
import logging
import json
import os
from dotenv import load_dotenv
from src.utils.config_loader import load_config

# Load environment variables
load_dotenv()

# The "Mega-Prompt" defining the Handler's Persona and Protocol
SYSTEM_PROMPT = """
You are the "Handler" for the flight simulator DCS World.
Your job is to translate natural language voice commands from the Pilot into specific JSON intents.

AIRCRAFT CONTEXT:
The pilot is flying the **OH-58D Kiowa Warrior**.
All commands apply to this aircraft.
The "aircraft" field in the JSON output MUST always be "OH-58D".

FLIGHT TERMINOLOGY:
- "Angels X" = X * 1000 feet (e.g., Angels 5 = 5000 ft).
- "Cherubs X" = X * 100 feet.
- "NNE", "South", etc. = Convert to degrees (N=0, NNE=22.5, E=90, S=180, W=270).

JSON SCHEMA:
{
  "aircraft": "OH-58D",
  "action": "string",   // e.g. "search_sector", "set_master_arm", "set_flight_parameters"
  "parameters": {       // Key-value pairs specific to the action
    "state": 1 or 0,    // For toggles
    "direction": "string",
    # For "set_flight_parameters":
    "heading": number,  // degrees
    "altitude": number, // feet
    "speed": number     // knots
  }
}

STRICT OUTPUT RULES:
1. Output ONLY valid JSON.
2. Output a SINGLE JSON Object.
3. If multiple parameters are given (heading + alt), include all in "parameters".

EXAMPLES:
Input: "Master arm on"
Output: {"aircraft": "OH-58D", "action": "set_master_arm", "parameters": {"state": 1}}

Input: "Take us up to angels 1.5 and head West at 60 knots"
Output: {"aircraft": "OH-58D", "action": "set_flight_parameters", "parameters": {"altitude": 1500, "heading": 270, "speed": 60}}
"""

class Brain:
    def __init__(self):
        self.config = load_config()
        
        # API Key Logic: Check Env Var first, then Config
        self.api_key = os.getenv("GEMINI_API_KEY") or self.config['brain'].get('api_key')
        
        if not self.api_key or "YOUR_API_KEY" in self.api_key:
            logging.error("No valid Gemini API Key found in env GEMINI_API_KEY or config.json")
            # We don't raise immediately to allow the app to start so user can see the error
        else:
            genai.configure(api_key=self.api_key)
            self.model_name = self.config['brain'].get('model', 'gemini-2.0-flash-exp')
            logging.info(f"Brain initialized with model: {self.model_name}")
            
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=SYSTEM_PROMPT,
                generation_config={"response_mime_type": "application/json"}
            )

    def think(self, text):
        """
        Sends text to Gemini and returns a JSON object (dict).
        """
        if not self.api_key or "YOUR_API_KEY" in self.api_key:
            logging.error("Cannot think: Missing API Key.")
            return None

        try:
            logging.info(f"Thinking about: '{text}'")
            # Generate content
            response = self.model.generate_content(text)
            
            # Parse JSON
            # Gemini 2.0 Flash is good at JSON mode, usually returns pure JSON.
            # We strip markdown code blocks just in case.
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:-3]
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:-3]
            
            intent = json.loads(clean_text)
            logging.info(f"Thought: {json.dumps(intent)}")
            return intent

        except Exception as e:
            logging.error(f"Brain freeze (Error): {e}")
            return None
