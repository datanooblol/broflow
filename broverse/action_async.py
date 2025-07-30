from typing import Dict, Any
import warnings
import asyncio

class BaseAsyncAction:
    def __init__(self):
        self.successors = {}
        self.next_action = 'default'
    
    def register_next_action(self, next_action, next_action_name: str) -> Any:
        if next_action_name in self.successors:
            warnings.warn(f"Action '{next_action_name}' overwritten.", stacklevel=2)
        self.successors[next_action_name] = next_action
        return next_action

    def get_next_action(self, next_action_name: str | None) -> Any:
        return self.successors.get(next_action_name, None)

    async def run_async(self, shared: Dict[str, Any]) -> Any:
        raise NotImplementedError("Overwrite .run_async method before starting AsyncFlow")
    
    def validate_next_action(self, shared: dict) -> str:
        return self.next_action

    async def execute_action(self, shared: Dict[str, Any]) -> str:
        """Run async action and return next_action_name"""
        result = await self.run_async(shared)
        return self.validate_next_action(result)

    def __sub__(self, next_action_name: str):
        if isinstance(next_action_name, str):
            next_action_name = "default" if next_action_name == "" else next_action_name
            return AsyncRelation(self, next_action_name)
        raise TypeError(f"next_action_name must be str, got {type(next_action_name)} instead")
    
    def __rshift__(self, next_action):
        return self.register_next_action(next_action, "default")


class AsyncAction(BaseAsyncAction):
    def __init__(self, max_retries=1, wait=0):
        super().__init__()
        self.max_retries = max_retries
        self.wait = wait

    async def run_async(self, shared: Dict[str, Any]) -> Any:
        for retry in range(self.max_retries):
            try:
                return await self._run_async(shared)
            except Exception as e:
                if retry == self.max_retries - 1:
                    return await self.run_fallback(shared, e)
                if self.wait > 0:
                    await asyncio.sleep(self.wait)

    async def _run_async(self, shared: Dict[str, Any]) -> Any:
        raise NotImplementedError("Overwrite ._run_async method")

    async def run_fallback(self, shared: Dict[str, Any], exc: Exception) -> Any:
        raise exc


class AsyncRelation:
    def __init__(self, action: BaseAsyncAction, next_action_name: str):
        self.action = action
        self.next_action_name = next_action_name
    
    def __rshift__(self, next_action):
        return self.action.register_next_action(next_action, self.next_action_name)


class AsyncStart(AsyncAction):
    def __init__(self, message):
        super().__init__()
        self.message = message
        
    async def _run_async(self, shared):
        print(self.message)
        return shared


class AsyncEnd(AsyncAction):
    def __init__(self, message):
        super().__init__()
        self.message = message

    async def _run_async(self, shared):
        print(self.message)
        return shared