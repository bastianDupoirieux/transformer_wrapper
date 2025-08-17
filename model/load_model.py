
"""
Test script for the ReviewClassifier model.
This file serves as a simple tester for the model functionality.
"""

import sys
import os

# Add src to path to import from the package
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.review_classifier import ReviewClassifier

def test_model():
    """Test the ReviewClassifier model with sample texts"""
    
    print("🧪 Testing ReviewClassifier model...")
    
    # Create model instance
    classifier = ReviewClassifier()
    
    # Test texts
    test_texts = [
        "Great place! I really enjoyed my time here, thank you for the great service!",
        "Terrible experience. The food was cold and the service was awful.",
        "It was okay, nothing special but not bad either.",
        "Amazing! Best restaurant I've ever been to!"
    ]
    
    print("\n📝 Running classification tests:")
    print("=" * 50)
    
    for i, text in enumerate(test_texts, 1):
        try:
            result = classifier.classify_text(text)
            print(f"Test {i}: {result}")
            print(f"Text: {text[:50]}...")
            print("-" * 30)
        except Exception as e:
            print(f"Test {i} failed: {e}")
    
    print("\n✅ Model testing completed!")

if __name__ == "__main__":
    test_model()
