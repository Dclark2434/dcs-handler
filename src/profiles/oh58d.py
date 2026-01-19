
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

    return f"{cmd_id} 1"
