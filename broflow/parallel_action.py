import copy
import asyncio
from broflow import Action

class ParallelAction(Action):
    def __init__(self, *actions, result_key='parallel'):
        super().__init__()
        self.actions = actions
        self.result_key = result_key
    
    def run(self, shared):
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
