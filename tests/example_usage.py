"""
Example usage of the Ray Wrapper for deploying custom models.

This script demonstrates how to:
1. Create custom models
2. Deploy them using the Ray wrapper
3. Make requests to the deployed models
"""

from ray import serve
from testWrapper import RayWrapper
import requests
import json

# Example 1: Custom Text Processing Model
class TextProcessor:
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model_path = model_path
        self.device = device
        print(f"Initialized TextProcessor with model: {model_path} on {device}")
    
    def process_text(self, text: str, max_length: int = 100):
        """Process text and return processed result"""
        return f"Processed: {text[:max_length]}"
    
    def summarize(self, text: str, max_words: int = 50):
        """Summarize text"""
        words = text.split()
        summary = " ".join(words[:max_words])
        return f"Summary: {summary}"
    
    def translate(self, text: str, target_language: str = "es"):
        """Translate text (mock implementation)"""
        return f"Translated to {target_language}: {text}"

# Example 2: ML Model Wrapper
class MLModel:
    def __init__(self, model_name: str, max_length: int = 512):
        self.model_name = model_name
        self.max_length = max_length
        print(f"Initialized MLModel: {model_name}")
    
    def forward(self, input_data: str):
        """Forward pass through the model"""
        return f"ML prediction for: {input_data}"
    
    def encode_text(self, text: str):
        """Encode text to embeddings"""
        return f"Encoded: {text[:self.max_length]}"
    
    def classify_text(self, text: str, num_classes: int = 3):
        """Classify text"""
        return f"Classification result: class_{hash(text) % num_classes}"

def deploy_with_config():
    """Deploy using configuration file"""
    # Start Ray Serve
    serve.start()
    
    # Deploy with configuration
    app = RayWrapper.bind("model_config.yml")
    
    print("Deployment started with configuration file")
    return app

def deploy_programmatically():
    """Deploy models programmatically"""
    # Start Ray Serve
    serve.start()
    
    # Create wrapper instance
    wrapper = RayWrapper.remote()
    
    # Register models programmatically
    text_processor = TextProcessor("/path/to/model", "cpu")
    wrapper.register_model.remote(
        "text_processor", 
        text_processor, 
        ["process_text", "summarize", "translate"]
    )
    
    ml_model = MLModel("bert-base-uncased", 512)
    wrapper.register_model.remote(
        "ml_model", 
        ml_model, 
        {
            "predict": "forward",
            "encode": "encode_text", 
            "classify": "classify_text"
        }
    )
    
    # Deploy
    app = wrapper.bind()
    
    print("Deployment started programmatically")
    return app

def test_deployment(app):
    """Test the deployed models"""
    base_url = "http://localhost:8000"
    
    # Test 1: List available models
    print("\n1. Listing available models:")
    response = requests.get(f"{base_url}/?action=list_models")
    print(json.dumps(response.json(), indent=2))
    
    # Test 2: Get function signature
    print("\n2. Getting function signature:")
    response = requests.get(f"{base_url}/?action=function_signature&model=text_processor&function=process_text")
    print(json.dumps(response.json(), indent=2))
    
    # Test 3: Call text processing function
    print("\n3. Calling text processing function:")
    data = {
        "model": "text_processor",
        "function": "process_text",
        "parameters": {
            "text": "This is a sample text for processing",
            "max_length": 20
        }
    }
    response = requests.post(f"{base_url}/", json=data)
    print(json.dumps(response.json(), indent=2))
    
    # Test 4: Call ML model function
    print("\n4. Calling ML model function:")
    data = {
        "model": "ml_model",
        "function": "predict",
        "parameters": {
            "input_data": "Sample input for ML model"
        }
    }
    response = requests.post(f"{base_url}/", json=data)
    print(json.dumps(response.json(), indent=2))
    
    # Test 5: Call with GET parameters
    print("\n5. Calling with GET parameters:")
    response = requests.get(f"{base_url}/?model=text_processor&function=summarize&parameters[text]=This is a very long text that needs to be summarized&parameters[max_words]=10")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Ray Wrapper Example Usage")
    print("=" * 50)
    
    # Choose deployment method
    method = input("Choose deployment method (1: config file, 2: programmatic): ")
    
    if method == "1":
        app = deploy_with_config()
    else:
        app = deploy_programmatically()
    
    # Test the deployment
    test_deployment(app)
    
    print("\nDeployment is running. Press Ctrl+C to stop.")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping deployment...")
        serve.shutdown()
