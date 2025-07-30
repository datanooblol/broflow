from broverse.action import BaseAction, Action
from typing import Dict, Any
import copy

class Flow(BaseAction):
    def __init__(self, start_action:Action, name:str | None=None):
        super().__init__()
        self.start_action:Action = start_action
        self.name = name or f"Flow_{id(self)}"

    def run(self, shared:Dict[str, Any]):
        current_action = copy.copy(self.start_action)
        next_action_name = None
        while current_action:
            action_name = current_action.__class__.__name__
            if action_name not in ["Start", "End"]:
                self.print(f"Running action: {action_name}")
            next_action_name = current_action.execute_action(shared)
            current_action = current_action.get_next_action(next_action_name)
        return next_action_name
    
    def to_mermaid(self):
        """Generate mermaid flowchart"""
        lines = ["```mermaid", "flowchart TD"]
        visited = set()
        
        def traverse(action:Action, action_name:str="start"):
            if id(action) in visited:
                return
            visited.add(id(action))
            
            for next_name, next_action in action.successors.items():
                if hasattr(next_action, 'name'):
                    next_action_name = next_action.name.replace(" ", "_")
                else:
                    next_action_name = next_action.__class__.__name__
                lines.append(f"    {action_name} -->|{next_name}| {next_action_name}")
                traverse(next_action, next_action_name)
        
        start_name = self.name.replace(" ", "_") if hasattr(self, 'name') else self.start_action.__class__.__name__
        traverse(self.start_action, start_name)
        lines.append("```")
        return "\n".join(lines)
    
    def save_mermaid(self, filename):
        """Save mermaid chart to .md file"""
        with open(filename, 'w') as f:
            f.write(self.to_mermaid())