import sys
import os

# Add the parent directory to Python path to import from root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from model import ReviewClassifier
from ray_wrapper import RayDeployment

def main():
    """Test the RayDeployment with ReviewClassifier"""
    
    print("🚀 Testing RayDeployment with ReviewClassifier...")
    
    # Create deployment
    deployment = RayDeployment(
        model_class=ReviewClassifier,
        stage="development"
    )
    
    # Deploy the model
    deployment_info = deployment.deploy_model()
    
    print(f"Deployment successful!")
    print(f"Deployment ID: {deployment_info['deployment_id']}")
    print(f"Endpoint: {deployment_info['endpoint']}")

if __name__ == "__main__":
    main()