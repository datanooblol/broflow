from typing import Dict, Any
import warnings
from broverse.state import state

class BaseAction:
    def __init__(self):
        self.successors = {}
        self.next_action = 'default'

    def print(self, message):
        if state.get('debug'):
            print(message)
    
    def register_next_action(self, next_action, next_action_name:str) -> Any:
        if next_action_name in self.successors:
            warnings.warn(f"Action '{next_action_name}' overwritten.", stacklevel=2)
        self.successors[next_action_name] = next_action
        return next_action
    
    def get_next_action(self, next_action_name:str | None) -> Any:
        return self.successors.get(next_action_name, None)

    def run(self, shared:Dict[str, Any]) -> Any:
        raise NotImplementedError("Overwrite .run method before starting Flow")
    
    def validate_next_action(self, shared:dict) -> str:
        return self.next_action

    def execute_action(self, shared:Dict[str, Any]) -> str:
        """Run action and return next_action_name"""
        result = self.run(shared)
        return self.validate_next_action(result)

    def __sub__(self, next_action_name:str):
        if isinstance(next_action_name, str):
            next_action_name = "default" if next_action_name=="" else next_action_name
            return Relation(self, next_action_name)
        raise TypeError(f"next_action_name must be str, got {type(next_action_name)} instead")
    
    def __rshift__(self, next_action):
        return self.register_next_action(next_action, "default")


class Action(BaseAction):
    def __init__(self, ):
        super().__init__()

    
class Relation:
    def __init__(self, action:BaseAction, next_action_name:str):
        self.action = action
        self.next_action_name = next_action_name
    def __rshift__(self, next_action):
        return self.action.register_next_action(next_action, self.next_action_name)
    
class Start(Action):
    def __init__(self, message):
        super().__init__()
        self.message = message
        
    def run(self, shared):
        print(self.message)
        return shared

class End(Action):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self, shared):
        print(self.message)
        return shared