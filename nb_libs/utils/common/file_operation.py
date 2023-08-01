import json

def write_to_json(target_path:str, data:dict):
    with open(target_path, 'w') as f:
        json.dump(data, f, indent=4)

def read_from_json(target_path:str):
    with open(target_path) as f:
        return json.load(f)