class GlobalState:
    _instance = None
    _state = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set(self, key, value):
        self._state[key] = value
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def update(self, **kwargs):
        self._state.update(kwargs)
    
    def clear(self):
        self._state.clear()
    
    def keys(self):
        return self._state.keys()
    
    def items(self):
        return self._state.items()

# Global instance
state = GlobalState()
state.set("debug", True)