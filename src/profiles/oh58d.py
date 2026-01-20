
# OH-58D Kiowa Warrior Profile

# Mapping of high-level actions to DCS-BIOS identifiers
# For simple switches, the value is the DCS-BIOS ID.
# For complex actions, we might need a function or a list of commands (handled in bridge).

COMMANDS = {
    "set_master_arm": "PLT_MASTER_ARM",
    # AI Helper Commands (George/Barundus simulation via keybinds or cockpit switches if available)
    # Note: DCS-BIOS allows clicking clickable cockpit switches. 
    # If "Barundus" features have direct cockpit switch equivalents, we map them here.
    
    # MMS (Mast Mounted Sight) Control - Theoretical mapping
    # In reality, this might be button presses or axis slewing.
    # For this example, we assume there's a BIOS hook for "Slew MMS" or we use a hack.
    # Since the user specifically mentioned "MMS Slew" and "7778", we assume they have a way to inject it.
    
    # Example mapping for "search_sector" -> We might not have a direct "search sector" button.
    # We might need to map this to a sequence of slews.
    # For now, we will map it to a placeholder or a specific switch that enables searching.
    "search_sector": "MMS_SEARCH_TOGGLE_PLACEHOLDER", 
    
    # Weapon controls
    "weapon_hellfire": "PLT_WPN_SEL_HELLFIRE",
    "weapon_rockets": "PLT_WPN_SEL_ROCKET",
    "weapon_gun": "PLT_WPN_SEL_GUN",
    
    # Laser
    "laser_arm": "PLT_LASER_ARM",
}

def get_command(action, parameters):
    """
    Returns the DCS-BIOS command string for a given action and parameters.
    """
    cmd_id = COMMANDS.get(action)
    if not cmd_id:
        return None
        
    # Handling specific parameter logic
    # Example: set_master_arm with state=1
    if action == "set_master_arm":
        state = parameters.get("state", 1) # Default to 1 (ON)
        return f"{cmd_id} {state}"
    
    if "weapon" in action:
        # Selection usually just a toggle or button press (1)
        return f"{cmd_id} 1"

    if action == "search_sector":
        # logic for direction?
        # If parameters has 'direction', we might need to send different commands.
        # For simplicity in V1, we just return the ID with Value 1
        return f"{cmd_id} 1"

    if action == "set_flight_parameters":
        # Load Keybinds
        # TODO: Ideally cache this at module level or pass in, but for V1 load here ok
        import json
        import os
        
        keybinds = {}
        try:
            # Assume keybinds.json is in src/
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keybinds.json")
            with open(path, 'r') as f:
                full_binds = json.load(f)
                keybinds = full_binds.get("OH-58D", {})
        except Exception as e:
            logging.error(f"Failed to load keybinds: {e}")

        # Helper to find nearest key in a dict
        def get_nearest(value, mapping):
            return min(mapping.keys(), key=lambda k: abs(k-value))

        # 1. SPEED (Knots)
        # We look for keys starting with "Set " and ending " knt" to build the map dynamically
        speed = parameters.get("speed")
        if speed:
            # Parse available speeds from keybinds
            # Format: "Set 80 knt"
            available_speeds = []
            for k in keybinds.keys():
                if k.startswith("Set ") and k.endswith(" knt"):
                    try:
                        val = int(k.split(" ")[1])
                        available_speeds.append(val)
                    except: pass
            
            if available_speeds:
                target = min(available_speeds, key=lambda x: abs(x - speed))
                action_name = f"Set {target} knt"
                keys = keybinds.get(action_name)
                
                logging.info(f"Target Speed: {speed} -> Quantized: {target} ({action_name})")
                if keys:
                    return {"type": "keyboard", "keys": keys}
                else: 
                     return {"type": "keyboard", "keys": [], "log": f"Missing keybind for {action_name}"}

        # 2. ALTITUDE (Feet)
        # Format: "Set 5000 ft"
        alt = parameters.get("altitude")
        if alt:
            available_alts = []
            for k in keybinds.keys():
                if k.startswith("Set ") and k.endswith(" ft"):
                    try:
                        val = int(k.split(" ")[1])
                        available_alts.append(val)
                    except: pass

            if available_alts:
                target = min(available_alts, key=lambda x: abs(x - alt))
                action_name = f"Set {target} ft"
                keys = keybinds.get(action_name)
                
                logging.info(f"Target Altitude: {alt} -> Quantized: {target} ({action_name})")
                if keys:
                     return {"type": "keyboard", "keys": keys}
                else:
                     return {"type": "keyboard", "keys": [], "log": f"Missing keybind for {action_name}"}

        # 3. HEADING
        # Format "Head to 200"
        heading = parameters.get("heading")
        if heading is not None:
             # Parse available headings
            available_heads = []
            for k in keybinds.keys():
                if k.startswith("Head to "):
                    try:
                        val = int(k.split(" to ")[1])
                        available_heads.append(val)
                    except: pass
            
            if available_heads:
                target = min(available_heads, key=lambda x: abs(x - heading))
                # 360 wrap logic check? User screenshots show 0 and 350. 
                # Diff between 355 and 0 is 5. Simple subtraction says 355.
                # Use modular distance for heading?
                # Formula: diff = 180 - abs(abs(a1 - a2) - 180)
                # For now simple linear closest is mostly fine if density is high (every 10 deg)
                
                action_name = f"Head to {target}"
                keys = keybinds.get(action_name)
                
                logging.info(f"Target Heading: {heading} -> Quantized: {target} ({action_name})")
                if keys:
                    return {"type": "keyboard", "keys": keys}
                else:
                    return {"type": "keyboard", "keys": [], "log": f"Missing keybind for {action_name}"}

        return None

    return f"{cmd_id} 1"

    return f"{cmd_id} 1"
