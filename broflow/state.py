class GlobalState:
    """Singleton class for managing global workflow state.
    
    Provides a centralized state store that can be accessed across
    all actions in a workflow.
    """
    _instance = None
    _state = {}
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern).
        
        Returns:
            The single GlobalState instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def set(self, key, value):
        """Set a key-value pair in the global state.
        
        Args:
            key: State key.
            value: State value.
        """
        self._state[key] = value
    
    def get(self, key, default=None):
        """Get a value from the global state.
        
        Args:
            key: State key to retrieve.
            default: Default value if key doesn't exist.
            
        Returns:
            The value associated with the key, or default if not found.
        """
        return self._state.get(key, default)
    
    def update(self, **kwargs):
        """Update multiple key-value pairs in the global state.
        
        Args:
            **kwargs: Key-value pairs to update.
        """
        self._state.update(kwargs)
    
    def clear(self):
        """Clear all key-value pairs from the global state."""
        self._state.clear()
    
    def keys(self):
        """Get all keys in the global state.
        
        Returns:
            Dictionary keys view.
        """
        return self._state.keys()
    
    def items(self):
        """Get all key-value pairs in the global state.
        
        Returns:
            Dictionary items view.
        """
        return self._state.items()

# Global instance
state = GlobalState()
state.set("debug", True)