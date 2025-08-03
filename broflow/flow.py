from broflow.action import BaseAction, Action
from typing import Dict, Any
import copy

class Flow(BaseAction):
    """Main workflow orchestrator that executes action sequences.
    
    Flow manages the execution of chained actions, handling state passing
    and conditional branching between actions.
    """
    def __init__(self, start_action:Action, name:str | None=None):
        """Initialize Flow with a starting action.
        
        Args:
            start_action: First action to execute in the workflow.
            name: Optional name for the flow. Defaults to Flow_{id}.
        """
        super().__init__()
        self.start_action:Action = start_action
        self.name = name or f"Flow_{id(self)}"

    def run(self, shared):
        """Execute the complete workflow starting from start_action.
        
        Args:
            shared: Initial shared state dictionary passed between actions.
            
        Returns:
            Name of the final action that was executed.
        """
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
        """Generate Mermaid flowchart representation of the workflow.
        
        Returns:
            String containing Mermaid flowchart syntax.
        """
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
        """Save Mermaid flowchart to a markdown file.
        
        Args:
            filename: Path to the output markdown file.
        """
        with open(filename, 'w') as f:
            f.write(self.to_mermaid())