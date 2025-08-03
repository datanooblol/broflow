from typing import Dict, Any
import warnings
from broflow.state import state

class BaseAction:
    """Base class for all actions in broflow workflows.
    
    Provides core functionality for action chaining, state management,
    and workflow execution.
    """
    def __init__(self):
        """Initialize BaseAction with empty successors and default next action."""
        self.successors = {}
        self.next_action = 'default'

    def print(self, message):
        """Print debug message if debug mode is enabled.
        
        Args:
            message: Message to print.
        """
        if state.get('debug'):
            print(message)
    
    def register_next_action(self, next_action, next_action_name:str) -> Any:
        """Register a successor action with a given name.
        
        Args:
            next_action: The action to register as successor.
            next_action_name: Name/key for the successor action.
            
        Returns:
            The registered next_action.
        """
        if next_action_name in self.successors:
            warnings.warn(f"Action '{next_action_name}' overwritten.", stacklevel=2)
        self.successors[next_action_name] = next_action
        return next_action
    
    def get_next_action(self, next_action_name:str | None) -> Any:
        """Get successor action by name.
        
        Args:
            next_action_name: Name of the successor action to retrieve.
            
        Returns:
            The successor action or None if not found.
        """
        return self.successors.get(next_action_name, None)

    def run(self, shared) -> Any:
        """Execute the action logic.
        
        Args:
            shared: Shared state dictionary or any data structure.
            
        Returns:
            Modified shared state or result data.
            
        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError("Overwrite .run method before starting Flow")
    
    def validate_next_action(self, shared) -> str:
        """Determine which successor action to execute next.
        
        Args:
            shared: Current shared state.
            
        Returns:
            Name of the next action to execute.
        """
        return self.next_action

    def execute_action(self, shared) -> str:
        """Execute action and determine next action name.
        
        Args:
            shared: Shared state dictionary.
            
        Returns:
            Name of the next action to execute.
        """
        result = self.run(shared)
        return self.validate_next_action(result)

    def __sub__(self, next_action_name:str):
        """Create a named relation for conditional branching.
        
        Args:
            next_action_name: Name for the conditional branch.
            
        Returns:
            Relation object for chaining.
            
        Raises:
            TypeError: If next_action_name is not a string.
        """
        if isinstance(next_action_name, str):
            next_action_name = "default" if next_action_name=="" else next_action_name
            return Relation(self, next_action_name)
        raise TypeError(f"next_action_name must be str, got {type(next_action_name)} instead")
    
    def __rshift__(self, next_action):
        """Chain actions using >> operator.
        
        Args:
            next_action: Action to chain after this one.
            
        Returns:
            The next_action for further chaining.
        """
        return self.register_next_action(next_action, "default")


class Action(BaseAction):
    """Standard action class for workflow steps.
    
    Inherits all functionality from BaseAction. Users should subclass
    this to create custom workflow actions.
    """
    
    def __init__(self, ):
        """Initialize Action."""
        super().__init__()

    
class Relation:
    """Represents a named relationship between actions for conditional branching."""
    
    def __init__(self, action:BaseAction, next_action_name:str):
        """Initialize relation.
        
        Args:
            action: Source action.
            next_action_name: Name of the conditional branch.
        """
        self.action = action
        self.next_action_name = next_action_name
        
    def __rshift__(self, next_action):
        """Register the target action for this named relation.
        
        Args:
            next_action: Action to execute for this branch.
            
        Returns:
            The registered next_action.
        """
        return self.action.register_next_action(next_action, self.next_action_name)
    
class Start(Action):
    """Starting action for workflows.
    
    Prints a message and passes through the shared state unchanged.
    """
    
    def __init__(self, message):
        """Initialize Start action.
        
        Args:
            message: Message to print when workflow starts.
        """
        super().__init__()
        self.message = message
        
    def run(self, shared):
        """Print start message and return shared state.
        
        Args:
            shared: Shared state dictionary.
            
        Returns:
            Unmodified shared state.
        """
        print(self.message)
        return shared

class End(Action):
    """Ending action for workflows.
    
    Prints a message and passes through the shared state unchanged.
    """
    
    def __init__(self, message):
        """Initialize End action.
        
        Args:
            message: Message to print when workflow ends.
        """
        super().__init__()
        self.message = message

    def run(self, shared):
        """Print end message and return shared state.
        
        Args:
            shared: Shared state dictionary.
            
        Returns:
            Unmodified shared state.
        """
        print(self.message)
        return shared