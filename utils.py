import json

def load_settings(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        settings = json.load(file)
    return settings