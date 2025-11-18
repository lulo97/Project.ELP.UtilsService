import json

def getConfig(key=None):
    file_path = "config.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(key)
