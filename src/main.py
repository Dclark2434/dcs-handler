import sys
import os
import json

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bridge import Bridge

def main():
    print("Initializing DCS-Handler Bridge...")
    bridge = Bridge()
    print("Bridge initialized.")
    print("Enter a command (e.g. 'Master Arm On') or raw JSON.")
    print("Type 'exit' to quit.")

    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ['exit', 'quit']:
                break
            
            # Simple heuristic: if it looks like JSON, treat as JSON.
            # Otherwise, we might act as a very dumb "text parser" for testing purposes
            # or just construct a fake JSON object to test the bridge.
            
            if user_input.strip().startswith("{"):
                bridge.process_intent(user_input)
            else:
                # Mocking the AI Brain part for testing
                print("Mocking AI Brain processing...")
                # Simple keyword matching for demo
                mock_intent = None
                if "master arm on" in user_input.lower():
                    mock_intent = {
                        "aircraft": "OH-58D",
                        "action": "set_master_arm",
                        "parameters": {"state": 1}
                    }
                elif "search" in user_input.lower():
                    mock_intent = {
                        "aircraft": "OH-58D",
                        "action": "search_sector",
                        "parameters": {"direction": "left"}
                    }
                
                if mock_intent:
                    print(f"Generated Intent: {json.dumps(mock_intent)}")
                    bridge.process_intent(mock_intent)
                else:
                    print("Could not understand command. Try valid JSON.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    bridge.close()
    print("Exiting.")

if __name__ == "__main__":
    main()
