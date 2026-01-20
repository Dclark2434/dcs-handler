import ctypes
import time
import logging

# Windows input structures
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_short)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Scancodes for DirectX/DCS
# incomplete list, added as needed
# https://www.win.tue.nl/~aeb/linux/kbd/scancodes-1.html
# Scancodes for DirectX/DCS
# Format: 'key': (scancode, is_extended)
# https://www.win.tue.nl/~aeb/linux/kbd/scancodes-1.html
SCANCODES = {
    'esc': (0x01, False), '1': (0x02, False), '2': (0x03, False), '3': (0x04, False), '4': (0x05, False), 
    '5': (0x06, False), '6': (0x07, False), '7': (0x08, False), '8': (0x09, False), '9': (0x0A, False), 
    '0': (0x0B, False), '-': (0x0C, False), '=': (0x0D, False), 'backspace': (0x0E, False), 
    'tab': (0x0F, False), 'q': (0x10, False), 'w': (0x11, False), 'e': (0x12, False), 'r': (0x13, False), 
    't': (0x14, False), 'y': (0x15, False), 'u': (0x16, False), 'i': (0x17, False), 'o': (0x18, False), 
    'p': (0x19, False), '[': (0x1A, False), ']': (0x1B, False), 'enter': (0x1C, False), 
    'lctrl': (0x1D, False), 'a': (0x1E, False), 's': (0x1F, False), 'd': (0x20, False), 'f': (0x21, False), 
    'g': (0x22, False), 'h': (0x23, False), 'j': (0x24, False), 'k': (0x25, False), 'l': (0x26, False), 
    ';': (0x27, False), "'": (0x28, False), '`': (0x29, False), 'lshift': (0x2A, False), 
    '\\': (0x2B, False), 'z': (0x2C, False), 'x': (0x2D, False), 'c': (0x2E, False), 'v': (0x2F, False), 
    'b': (0x30, False), 'n': (0x31, False), 'm': (0x32, False), ',': (0x33, False), '.': (0x34, False), 
    '/': (0x35, False), 'rshift': (0x36, False), 'kp_*': (0x37, False), 'lalt': (0x38, False), 
    'space': (0x39, False), 'capslock': (0x3A, False), 
    'f1': (0x3B, False), 'f2': (0x3C, False), 'f3': (0x3D, False), 'f4': (0x3E, False), 'f5': (0x3F, False),
    'f6': (0x40, False), 'f7': (0x41, False), 'f8': (0x42, False), 'f9': (0x43, False), 'f10': (0x44, False),
    'up': (0xC8, True), 'left': (0xCB, True), 'right': (0xCD, True), 'down': (0xD0, True),
    
    # Missing Modifiers
    'ralt': (0x38, True),
    'rctrl': (0x1D, True),
    'lwin': (0xDB, True), # 0xDB is typically just Left Windows key? Actually 0xE0 0x5B usually. 
                          # Wait, standard set 1 scancode for LWin is E0 5B.
                          # But DirectX/User32 uses standard codes. 
                          # MapVirtualKey(VK_LWIN, MAPVK_VK_TO_VSC) -> ?
                          # Using 0xDB might be wrong. 0x5B is VKEY. 
                          # Correct Scancode for LWin is usually 0xE0 5B. So (0x5B, True).
                          # Let's try (0x5B, True).
    'lwin': (0x5B, True), 
}

# C Wrapper functions
SendInput = ctypes.windll.user32.SendInput

class InputEmitter:
    def __init__(self):
        logging.info("InputEmitter initialized (DirectX/Win32).")

    def _send_input(self, hexKeyCode, press=True, extended=False):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        
        flags = 0x0008 # KEYEVENTF_SCANCODE
        if not press:
            flags |= 0x0002 # KEYEVENTF_KEYUP
        if extended:
            flags |= 0x0001 # KEYEVENTF_EXTENDEDKEY

        ii_.ki = KeyBdInput(0, hexKeyCode, flags, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def press_key(self, key_name, duration=0.1):
        """Presses and releases a key by name."""
        entry = SCANCODES.get(key_name.lower())
        if entry:
            code, ext = entry
            self._send_input(code, press=True, extended=ext)
            time.sleep(duration)
            self._send_input(code, press=False, extended=ext)
        else:
            logging.error(f"Unknown key: {key_name}")

    def press_combo(self, keys):
        """
        Presses a combination of keys e.g., ['lalt', 'a'].
        Holds all down, then releases in reverse order.
        """
        active_codes = []
        
        # Press all
        for k in keys:
            entry = SCANCODES.get(k.lower())
            if entry:
                code, ext = entry
                self._send_input(code, press=True, extended=ext)
                active_codes.append((code, ext))
                time.sleep(0.05)
            else:
                logging.error(f"Unknown key in combo: {k}")
                # We continue to try pressing others? or abort? 
                # Abort helps debugging.
                # But we should release what we pressed.
                pass 
        
        time.sleep(0.1) # Hold brief moment

        # Release all (reverse)
        for code, ext in reversed(active_codes):
            self._send_input(code, press=False, extended=ext)
            time.sleep(0.05)
            
        logging.info(f"Executed key combo: {keys}")
