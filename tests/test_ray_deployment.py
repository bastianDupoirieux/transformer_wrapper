"""
Test script for Ray ray_wrapper functionality.
This file tests the RayDeployment class with the ReviewClassifier.
"""

import sys
import os

# Add src to path to import from the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from review_classifier import ReviewClassifier
from deployment.ray_wrapper import RayDeployment

def test_ray_deployment():
    """Test the RayDeployment with ReviewClassifier"""
    
    print("🚀 Testing RayDeployment with ReviewClassifier...")
    
    # Create ray_wrapper
    deployment = RayDeployment(
        model_class=ReviewClassifier,
        stage="development"
    )
    
    # Deploy the model
    deployment_info = deployment.deploy_model()
    
    print(f"\n✅ Deployment successful!")
    print(f"📋 Deployment ID: {deployment_info['deployment_id']}")
    print(f"🌐 Endpoint: {deployment_info['endpoint']}")
    print(f"🏷️  Stage: {deployment_info['stage']}")
    
    print(f"\n📝 You can now test with:")
    print(f"curl '{deployment_info['endpoint']}?text=Great%20service!'")

if __name__ == "__main__":
    test_ray_deployment()
