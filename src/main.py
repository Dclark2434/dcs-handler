import sys
import os
import json
import logging

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bridge import Bridge
from src.ears import Ears
from src.brain import Brain

def main():
    print("Initializing DCS-Handler...")
    bridge = Bridge()
    
    ears = None
    try:
        ears = Ears()
        print(f"Ears initialized (Backend: {ears.backend.upper()}).")
    except Exception as e:
        print(f"Could not initialize Ears: {e}")

    brain = None
    try:
        brain = Brain()
        if brain.api_key and "YOUR_API_KEY" not in brain.api_key:
            print(f"Brain initialized (Model: {brain.model_name}).")
        else:
            print("Brain initialized but API Key is missing/default. Config required.")
    except Exception as e:
        print(f"Could not initialize Brain: {e}")

    print("\nModes:")
    print("1. Type a command (e.g. 'search left' or JSON)")
    print("2. Type 'listen' to record one phrase")
    print("3. Type 'loop' to continuously listen")
    print("Type 'exit' to quit.")

    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            intent_text = user_input

            # Handle Voice Modes
            if user_input.lower() in ['listen', '2']:
                if ears:
                    print("Listening... (Speak now)")
                    intent_text = ears.listen()
                    if not intent_text:
                        continue
                else:
                    print("Ears not available.")
                    continue

            elif user_input.lower() in ['loop', '3']:
                if ears:
                    print("Entering Voice Loop. Press Ctrl+C to stop.")
                    try:
                        while True:
                            print("Listening...")
                            intent_text = ears.listen()
                            if intent_text:
                                process_text(bridge, brain, intent_text)
                    except KeyboardInterrupt:
                        print("Exiting Voice Loop.")
                        continue
                else:
                    print("Ears not available.")
                    continue

            # Process the text (Typed or Spoken)
            process_text(bridge, brain, intent_text)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    bridge.close()
    print("Exiting.")

def process_text(bridge, brain, text):
    if not text:
        return

    print(f"Processing: '{text}'")
    
    # 1. Try JSON (Direct passthrough)
    if text.strip().startswith("{"):
        bridge.process_intent(text)
        return

    # 2. Use Brain (Gemini)
    if brain and brain.api_key and "YOUR_API_KEY" not in brain.api_key:
        print("Thinking...")
        intent = brain.think(text)
        if intent:
            # intent is already a dict
            print(f"Intent: {json.dumps(intent, indent=2)}")
            bridge.process_intent(intent)
        else:
            print("Brain returned nothing.")
    else:
        print("Brain is offline (Missing API Key). Using Mock Fallback for testing...")
        # Fallback Mock Logic
        mock_intent = None
        text_lower = text.lower()
        if "master arm on" in text_lower:
            mock_intent = {"aircraft": "OH-58D", "action": "set_master_arm", "parameters": {"state": 1}}
        
        if mock_intent:
            print(f"Mock Intent: {json.dumps(mock_intent)}")
            bridge.process_intent(mock_intent)
        else:
            print("Mock Brain: No match.")

if __name__ == "__main__":
    main()
