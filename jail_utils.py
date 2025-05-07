import json
import os

JAIL_DATA_FILE = "punishment_data.json"

def load_jail_data():
    if os.path.exists(JAIL_DATA_FILE):
        with open(JAIL_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_jail_data(data):
    with open(JAIL_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def store_user_roles(user_id, role_ids):
    data = load_jail_data()
    data[str(user_id)] = role_ids
    save_jail_data(data)

def retrieve_user_roles(user_id):
    data = load_jail_data()
    return data.pop(str(user_id), [])

def remove_user_from_jail_data(user_id):
    data = load_jail_data()
    data.pop(str(user_id), None)
    save_jail_data(data)
