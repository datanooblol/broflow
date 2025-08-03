import copy
import asyncio
from broflow.action import Action
from typing import Dict, Any


class ParallelAction(Action):
    """Execute multiple actions simultaneously in parallel.
    
    Uses asyncio to run multiple actions concurrently, collecting
    their results and storing them in the shared state.
    """
    def __init__(self, *actions, result_key='parallel'):
        """Initialize ParallelAction with multiple actions to run concurrently.
        
        Args:
            *actions: Variable number of Action instances to run in parallel.
            result_key: Key in shared state where results will be stored.
                       Defaults to 'parallel'.
        """
        super().__init__()
        self.actions = actions
        self.result_key = result_key
    
    def run(self, shared):
        """Execute all actions in parallel and collect results.
        
        Args:
            shared: Shared state dictionary passed to all parallel actions.
            
        Returns:
            Modified shared state with parallel execution results.
        """
        async def run_parallel():
            tasks = []
            for action in self.actions:
                action_copy = copy.copy(action)
                task = asyncio.to_thread(action_copy.run, shared)
                tasks.append(task)
            return await asyncio.gather(*tasks)
        
        results = asyncio.run(run_parallel())
        
        # Store results
        if self.result_key not in shared:
            shared[self.result_key] = {}
        
        for i, result in enumerate(results):
            if result:
                action_name = self.actions[i].__class__.__name__.lower()
                shared[self.result_key][action_name] = result       
        return shared
