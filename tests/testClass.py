class MyDeployment:
    def __init__(self, name: str):
        self._name = name

    def say_hello(self, name: str = None):
        """Say hello to a specific name or use the default name"""
        if name:
            return f"Hello {name}"
        return f"Hello {self._name}"
    
    def say_goodbye(self, name: str = None):
        """Say goodbye to a specific name or use the default name"""
        if name:
            return f"Goodbye {name}"
        return f"Goodbye {self._name}"
    
    def get_info(self):
        """Get information about the deployment"""
        return {
            "name": self._name,
            "type": "MyDeployment",
            "available_functions": ["say_hello", "say_goodbye", "get_info"]
        }