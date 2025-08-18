from ray import serve
from starlette.requests import Request
import json
from typing import Dict, Any, Callable, Optional, Union
import importlib
import inspect
from pathlib import Path
import yaml

@serve.deployment
class RayWrapper:
    """
    Generic Ray wrapper for deploying any model with custom functions.
    Supports dynamic model loading and function registration.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the wrapper with optional configuration file.
        
        Args:
            config_path: Path to YAML configuration file defining models and functions
        """
        self.models = {}
        self.model_functions = {}
        self.model_configs = {}
        
        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """Load model configurations from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            for model_config in config.get('models', []):
                self.register_model_from_config(model_config)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
    
    def register_model_from_config(self, model_config: Dict[str, Any]):
        """Register a model from configuration dictionary"""
        model_name = model_config['name']
        model_class_path = model_config['class_path']
        model_init_params = model_config.get('init_params', {})
        functions = model_config.get('functions', [])
        
        # Import and instantiate the model
        model_instance = self._import_and_instantiate(model_class_path, model_init_params)
        
        # Register the model
        self.register_model(model_name, model_instance, functions)
        
        # Store configuration
        self.model_configs[model_name] = model_config
    
    def _import_and_instantiate(self, class_path: str, init_params: Dict[str, Any]) -> Any:
        """Import a class and create an instance"""
        try:
            # Parse class path (e.g., "module.submodule.ClassName")
            module_path, class_name = class_path.rsplit('.', 1)
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the class
            model_class = getattr(module, class_name)
            
            # Create instance
            return model_class(**init_params)
            
        except Exception as e:
            raise ValueError(f"Failed to import and instantiate {class_path}: {e}")
    
    def register_model(self, model_name: str, model_instance: Any, functions: Union[list, Dict[str, str]]):
        """
        Register a model and its functions.
        
        Args:
            model_name: Name to identify the model
            model_instance: The model instance
            functions: List of function names or dict mapping function names to method names
        """
        self.models[model_name] = model_instance
        
        # Handle different function specification formats
        if isinstance(functions, list):
            # List of function names - assume they match method names
            self.model_functions[model_name] = {
                func_name: getattr(model_instance, func_name)
                for func_name in functions
                if hasattr(model_instance, func_name)
            }
        elif isinstance(functions, dict):
            # Dict mapping function names to method names
            self.model_functions[model_name] = {
                func_name: getattr(model_instance, method_name)
                for func_name, method_name in functions.items()
                if hasattr(model_instance, method_name)
            }
        else:
            # Auto-discover public methods
            self.model_functions[model_name] = {
                name: getattr(model_instance, name)
                for name in dir(model_instance)
                if callable(getattr(model_instance, name)) and not name.startswith('_')
            }
    
    def unregister_model(self, model_name: str):
        """Remove a model and its functions"""
        if model_name in self.models:
            del self.models[model_name]
            del self.model_functions[model_name]
            if model_name in self.model_configs:
                del self.model_configs[model_name]
    
    def list_models(self) -> Dict[str, Any]:
        """Return information about all registered models"""
        return {
            model_name: {
                "type": type(model).__name__,
                "functions": list(functions.keys()),
                "config": self.model_configs.get(model_name, {})
            }
            for model_name, model in self.models.items()
            for functions in [self.model_functions.get(model_name, {})]
        }
    
    def get_function_signature(self, model_name: str, function_name: str) -> Dict[str, Any]:
        """Get function signature and documentation"""
        if model_name not in self.model_functions:
            return {"error": f"Model '{model_name}' not found"}
        
        if function_name not in self.model_functions[model_name]:
            return {"error": f"Function '{function_name}' not found"}
        
        func = self.model_functions[model_name][function_name]
        sig = inspect.signature(func)
        
        return {
            "name": function_name,
            "signature": str(sig),
            "parameters": list(sig.parameters.keys()),
            "doc": func.__doc__ or "No documentation available"
        }
    
    async def __call__(self, request: Request):
        """Handle incoming requests"""
        try:
            # Get request data
            if request.method == "POST":
                data = await request.json()
            else:
                data = dict(request.query_params)
            
            # Handle special actions
            action = data.get("action")
            if action == "list_models":
                return {"models": self.list_models()}
            elif action == "function_signature":
                model_name = data.get("model")
                function_name = data.get("function")
                if model_name and function_name:
                    return self.get_function_signature(model_name, function_name)
                else:
                    return {"error": "Both 'model' and 'function' parameters required for function_signature action"}
            
            # Extract model and function from request
            model_name = data.get("model")
            function_name = data.get("function")
            parameters = data.get("parameters", {})
            
            # Validate required parameters
            if not model_name:
                return {"error": "Model name is required", "available_models": list(self.models.keys())}
            
            if not function_name:
                return {"error": "Function name is required"}
            
            # Validate model and function exist
            if model_name not in self.models:
                return {
                    "error": f"Model '{model_name}' not found", 
                    "available_models": list(self.models.keys())
                }
            
            if function_name not in self.model_functions.get(model_name, {}):
                return {
                    "error": f"Function '{function_name}' not found for model '{model_name}'", 
                    "available_functions": list(self.model_functions[model_name].keys())
                }
            
            # Get the target function
            target_function = self.model_functions[model_name][function_name]
            
            # Call the function with parameters
            try:
                if parameters:
                    result = target_function(**parameters)
                else:
                    result = target_function()
                
                return {
                    "result": result, 
                    "model": model_name, 
                    "function": function_name,
                    "parameters": parameters
                }
                
            except TypeError as e:
                # Function signature mismatch
                sig = inspect.signature(target_function)
                return {
                    "error": f"Function signature mismatch: {e}",
                    "expected_signature": str(sig),
                    "provided_parameters": parameters
                }
            
        except Exception as e:
            return {"error": str(e), "type": type(e).__name__}

# Create the deployment
app = RayWrapper.bind()

