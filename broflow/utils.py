from datetime import datetime, timezone

def get_timestamp():
    dt = datetime.now(timezone.utc)
    return dt.isoformat()

def load_prompt_yaml(file_path:str)->str:
    """This function will load a raw text instead of dictionary from yaml file"""
    with open(file_path, 'r') as f:
        data = f.read()
    return data