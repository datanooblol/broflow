import json
import yaml
from pathlib import Path
from .state import state

def load_config(file_path, format='auto'):
    """Load config from file and update global state"""
    path = Path(file_path)
    
    if format == 'auto':
        format = path.suffix.lower()
    
    with open(path, 'r') as f:
        if format in ['.json']:
            config = json.load(f)
        elif format in ['.yaml', '.yml']:
            config = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    state.update(**config)
    return config

def save_config(file_path, format='auto'):
    """Save current state to config file"""
    path = Path(file_path)
    
    if format == 'auto':
        format = path.suffix.lower()
    
    config = dict(state.items())
    
    with open(path, 'w') as f:
        if format in ['.json']:
            json.dump(config, f, indent=2)
        elif format in ['.yaml', '.yml']:
            yaml.dump(config, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}")