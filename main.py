"""
Main entry point for the transformer_wrapper application.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.review_classifier import ReviewClassifier
from deployment.ray_wrapper import RayDeployment

def main():
    """Main function to run the application"""
    
    print("🎯 Transformer Wrapper - Main Application")
    print("=" * 40)
    
    # Test the model first
    print("\n1️⃣ Testing model functionality...")
    classifier = ReviewClassifier()
    test_result = classifier.classify_text("Great service!")
    print(f"   Test result: {test_result}")
    
    # Deploy with Ray
    print("\n2️⃣ Deploying model with Ray...")
    deployment = RayDeployment(
        model_class=ReviewClassifier,
        stage="development"
    )
    
    deployment_info = deployment.deploy_model()
    
    print(f"\n✅ Application ready!")
    print(f"🌐 Endpoint: {deployment_info['endpoint']}")
    print(f"📋 Deployment ID: {deployment_info['deployment_id']}")
    
    print(f"\n📝 Test your deployment:")
    print(f"curl '{deployment_info['endpoint']}?text=Amazing%20experience!'")

if __name__ == "__main__":
    main()
