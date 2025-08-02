import json
import yaml
from pathlib import Path
from .state import state

def load_config(file_path:str)->dict:
    """Load configuration from file and update global state.
    
    Args:
        file_path: Path to the configuration file (.json, .yaml, or .yml).
               
    Returns:
        dict : Dictionary containing the loaded configuration.
        
    Raises:
        ValueError: If the file format is not supported.
    """
    path = Path(file_path)
    format = path.suffix.lower()
    
    with open(path, 'r') as f:
        if format == '.json':
            config = json.load(f)
        elif format in ['.yaml', '.yml']:
            config = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported format: {format}. Use .json, .yaml, or .yml")
    
    state.update(**config)
    return config

def save_config(file_path:str)->dict:
    """Save current global state to configuration file.
    
    Args:
        file_path: Path where the configuration file will be saved (.json, .yaml, or .yml).
    
    Returns:     
        dict : Dictionary containing current config
    Raises:
        ValueError: If the file format is not supported.
    """
    path = Path(file_path)
    format = path.suffix.lower()
    config = dict(state.items())
    
    # Create parent directories if they don't exist
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        if format == '.json':
            json.dump(config, f, indent=2)
        elif format in ['.yaml', '.yml']:
            yaml.dump(config, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported format: {format}. Use .json, .yaml, or .yml")
    return config