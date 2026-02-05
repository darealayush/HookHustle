import json
import os

def load_json(filename: str, default: dict) -> dict:
    if not os.path.exists(filename):
        save_json(filename, default)
        return default
    with open(filename, "r") as f:
        return json.load(f)

def save_json(filename: str, data: dict):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
