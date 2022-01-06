import json

JSON = ""
def load_json(PATH):
    with open(PATH) as f:
        JSON = json.load(f)
        return JSON
