#!/usr/bin/env python3
"""
Basic Usage Example for Baseline Generator

This example demonstrates the core functionality:
1. Creating a baseline
2. Testing against an existing baseline
3. Handling mismatches
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import baseline_generator
sys.path.insert(0, str(Path(__file__).parent.parent))

from baseline_generator import BaselineGenerator, BaselineComparisonError, BaselineNotFoundError


def main():
    print("=== Basic Baseline Generator Usage ===\n")
    
    # Initialize the generator with examples directory
    generator = BaselineGenerator("examples/test_baselines")
    
    # Example 1: Create a simple baseline
    print("1. Creating a simple baseline...")
    simple_data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "active": True
    }
    
    try:
        generator.generate_baseline("user_profile", simple_data)
        print("✓ Baseline 'user_profile.json' created successfully")
    except FileExistsError as e:
        print(f"✓ Baseline already exists: {e}")
    
    # Example 2: Test against the baseline with matching data
    print("\n2. Testing with matching data...")
    try:
        generator.test_against_baseline("user_profile", simple_data)
        print("✓ Data matches baseline perfectly!")
    except BaselineComparisonError as e:
        print(f"✗ Unexpected mismatch: {e}")
    
    # Example 3: Test with different data
    print("\n3. Testing with modified data...")
    modified_data = {
        "name": "Jane Doe",  # Changed name
        "age": 25,           # Changed age
        "email": "john@example.com",
        "active": True
    }
    
    try:
        generator.test_against_baseline("user_profile", modified_data)
        print("✓ Data matches baseline")
    except BaselineComparisonError as e:
        print(f"✗ Expected mismatch detected:")
        for diff in e.differences:
            print(f"   - {diff}")
    
    # Example 4: Test with missing fields
    print("\n4. Testing with missing fields...")
    incomplete_data = {
        "name": "John Doe",
        "age": 30
        # Missing email and active fields
    }
    
    try:
        generator.test_against_baseline("user_profile", incomplete_data)
        print("✓ Data matches baseline")
    except BaselineComparisonError as e:
        print(f"✗ Missing fields detected:")
        for diff in e.differences:
            print(f"   - {diff}")
    
    # Example 5: Test with extra fields
    print("\n5. Testing with extra fields...")
    extended_data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "active": True,
        "phone": "+1-555-0123",  # Extra field
        "address": "123 Main St"  # Extra field
    }
    
    try:
        generator.test_against_baseline("user_profile", extended_data)
        print("✓ Data matches baseline")
    except BaselineComparisonError as e:
        print(f"✗ Extra fields detected:")
        for diff in e.differences:
            print(f"   - {diff}")
    
    # Example 6: Auto-create missing baseline
    print("\n6. Testing auto-creation of missing baseline...")
    new_data = {
        "product": "Widget",
        "price": 29.99,
        "in_stock": True
    }
    
    try:
        generator.test_against_baseline("product_info", new_data)
        print("✓ Data matches baseline")
    except BaselineNotFoundError as e:
        print(f"✓ New baseline created: {e.message}")
        print(f"   Location: {e.baseline_path}")
    
    print("\n=== Example completed! ===")
    print("Check the 'examples/test_baselines/' directory to see the generated baseline files.")


if __name__ == "__main__":
    main() 