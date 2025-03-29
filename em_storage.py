import os
import pickle

def save_scratchpad(emulator):
    """Save scratchpad memory to a file."""
    try:
        with open("scratchpad.dat", "wb") as f:
            pickle.dump(emulator.scratchpad, f)
    except Exception as e:
        print(f"Error saving scratchpad: {e}")
    
def load_scratchpad(emulator):
    """Load scratchpad memory from a file, if it exists."""
    if os.path.exists("scratchpad.dat"):
        try:
            with open("scratchpad.dat", "rb") as f:
                emulator.scratchpad = pickle.load(f)
        except Exception as e:
            print(f"Error loading scratchpad: {e}")