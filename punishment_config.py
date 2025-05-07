# punishment_config.py

PUNISHMENT_MODE = {"mode": "jail"}  # or "timeout"

def get_mode():
    return PUNISHMENT_MODE["mode"]

def toggle_punishment_mode():
    PUNISHMENT_MODE["mode"] = "timeout" if PUNISHMENT_MODE["mode"] == "jail" else "jail"
    return PUNISHMENT_MODE["mode"]
