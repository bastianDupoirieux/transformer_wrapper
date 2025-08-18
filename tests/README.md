# Ray Wrapper for Dynamic Model Deployment

This Ray wrapper allows you to deploy any Python model with custom functions dynamically. It provides a flexible interface for serving machine learning models, text processors, or any custom Python classes.

## Features

- **Dynamic Model Loading**: Load models from configuration files or programmatically
- **Flexible Function Registration**: Expose specific methods or auto-discover all public methods
- **Parameter Validation**: Automatic function signature checking and error reporting
- **Multiple Deployment Methods**: Support for both configuration-based and programmatic deployment
- **RESTful API**: Simple HTTP interface for model inference
- **Function Signature Discovery**: Get function documentation and parameter requirements

## Quick Start

### 1. Basic Usage

```python
from ray import serve
from testWrapper import RayWrapper

# Start Ray Serve
serve.start()

# Deploy the wrapper
app = RayWrapper.bind()

# Your deployment is now running at http://localhost:8000
```

### 2. Using Configuration File

Create a `model_config.yml` file:

```yaml
models:
  - name: "my_model"
    class_path: "my_module.MyModel"
    init_params:
      model_path: "/path/to/model"
      device: "cuda"
    functions:
      - "predict"
      - "encode"
      - "classify"
```

Deploy with configuration:

```python
app = RayWrapper.bind("model_config.yml")
```

### 3. Programmatic Deployment

```python
from ray import serve
from testWrapper import RayWrapper

# Start Ray Serve
serve.start()

# Create wrapper
wrapper = RayWrapper.remote()

# Register your model
my_model = MyModel("/path/to/model")
wrapper.register_model.remote(
    "my_model", 
    my_model, 
    ["predict", "encode", "classify"]
)

# Deploy
app = wrapper.bind()
```

## API Reference

### HTTP Endpoints

#### List Available Models
```bash
GET /?action=list_models
```

Response:
```json
{
  "models": {
    "my_model": {
      "type": "MyModel",
      "functions": ["predict", "encode", "classify"],
      "config": {...}
    }
  }
}
```

#### Get Function Signature
```bash
GET /?action=function_signature&model=my_model&function=predict
```

Response:
```json
{
  "name": "predict",
  "signature": "(self, input_data: str, max_length: int = 100)",
  "parameters": ["input_data", "max_length"],
  "doc": "Make prediction on input data"
}
```

#### Call Model Function (GET)
```bash
GET /?model=my_model&function=predict&parameters[input_data]=hello&parameters[max_length]=50
```

#### Call Model Function (POST)
```bash
POST /
Content-Type: application/json

{
  "model": "my_model",
  "function": "predict",
  "parameters": {
    "input_data": "hello",
    "max_length": 50
  }
}
```

Response:
```json
{
  "result": "prediction_result",
  "model": "my_model",
  "function": "predict",
  "parameters": {
    "input_data": "hello",
    "max_length": 50
  }
}
```

### Python API

#### RayWrapper Class

```python
class RayWrapper:
    def __init__(self, config_path: Optional[str] = None)
    
    def load_config(self, config_path: str)
    def register_model(self, model_name: str, model_instance: Any, functions: Union[list, Dict[str, str]])
    def unregister_model(self, model_name: str)
    def list_models(self) -> Dict[str, Any]
    def get_function_signature(self, model_name: str, function_name: str) -> Dict[str, Any]
```

## Model Requirements

Your model class should:

1. **Have a constructor** that accepts initialization parameters
2. **Expose public methods** that can be called via HTTP requests
3. **Handle parameters properly** (the wrapper will pass them as keyword arguments)

Example model:

```python
class MyModel:
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        # Initialize your model here
    
    def predict(self, input_data: str, max_length: int = 100):
        """Make prediction on input data"""
        # Your prediction logic here
        return f"Prediction for: {input_data[:max_length]}"
    
    def encode(self, text: str):
        """Encode text to embeddings"""
        # Your encoding logic here
        return f"Encoded: {text}"
```

## Configuration File Format

The YAML configuration file supports the following structure:

```yaml
models:
  - name: "model_name"                    # Required: Unique identifier
    class_path: "module.ClassName"        # Required: Python import path
    init_params:                          # Optional: Constructor parameters
      param1: "value1"
      param2: "value2"
    functions:                            # Optional: List of functions or mapping
      - "function1"
      - "function2"
      # OR
      api_name: "method_name"             # Map API name to method name

settings:                                 # Optional: Global settings
  default_model: "model_name"
  timeout: 30
```

## Error Handling

The wrapper provides comprehensive error handling:

- **Model not found**: Returns available models
- **Function not found**: Returns available functions for the model
- **Parameter mismatch**: Returns expected function signature
- **Import errors**: Detailed error messages for configuration issues

## Examples

See `example_usage.py` for complete examples including:

- Text processing models
- ML model wrappers
- Configuration-based deployment
- Programmatic deployment
- Testing the deployment

## Running the Deployment

### Using Ray Serve CLI
```bash
serve run testWrapper:app
```

### Using Python
```python
from ray import serve
from testWrapper import RayWrapper

serve.start()
app = RayWrapper.bind()
# Deployment runs until you stop it
```

### Testing with curl
```bash
# List models
curl "http://localhost:8000/?action=list_models"

# Call function
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"model": "my_model", "function": "predict", "parameters": {"input_data": "test"}}'
```

## Advanced Usage

### Custom Model Classes

You can create any Python class and expose its methods:

```python
class CustomProcessor:
    def __init__(self, config):
        self.config = config
    
    def process(self, data, options=None):
        # Your processing logic
        return processed_data
    
    def analyze(self, data):
        # Your analysis logic
        return analysis_result

# Register with wrapper
wrapper.register_model.remote("processor", CustomProcessor({}), ["process", "analyze"])
```

### Function Name Mapping

Map API function names to different method names:

```python
wrapper.register_model.remote(
    "my_model", 
    model_instance, 
    {
        "predict": "forward",           # API name -> method name
        "encode": "encode_text",
        "classify": "classify_text"
    }
)
```

### Auto-discovery

Let the wrapper discover all public methods:

```python
wrapper.register_model.remote("my_model", model_instance, [])
# All public methods (not starting with _) will be available
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure your model class is importable from the specified path
2. **Parameter Mismatch**: Check function signatures and provide correct parameters
3. **Method Not Found**: Ensure the method exists and is public (doesn't start with `_`)

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

To extend the wrapper:

1. Add new features to the `RayWrapper` class
2. Update the configuration format if needed
3. Add tests for new functionality
4. Update documentation

## License

This wrapper is provided as-is for educational and development purposes.
