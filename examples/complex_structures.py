#!/usr/bin/env python3
"""
Complex Data Structures Example for Baseline Generator

This example demonstrates handling of:
1. Nested dictionaries
2. Lists with various data types
3. Mixed complex structures
4. Deep nesting scenarios
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import baseline_generator
sys.path.insert(0, str(Path(__file__).parent.parent))

from baseline_generator import BaselineGenerator, BaselineComparisonError, BaselineNotFoundError


def main():
    print("=== Complex Data Structures Example ===\n")
    
    # Initialize the generator
    generator = BaselineGenerator("examples/test_baselines")
    
    # Example 1: Nested dictionaries and lists
    print("1. Testing nested data structures...")
    complex_data = {
        "user": {
            "id": 12345,
            "profile": {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "preferences": {
                    "theme": "dark",
                    "notifications": True,
                    "language": "en"
                }
            },
            "roles": ["admin", "moderator"],
            "permissions": {
                "read": True,
                "write": True,
                "delete": False
            }
        },
        "session": {
            "id": "sess_abc123",
            "created_at": "2024-01-15T10:30:00Z",
            "expires_at": "2024-01-15T22:30:00Z",
            "active": True
        },
        "metadata": {
            "version": "1.0",
            "tags": ["production", "verified"],
            "metrics": {
                "login_count": 42,
                "last_activity": "2024-01-15T10:25:00Z"
            }
        }
    }
    
    try:
        generator.test_against_baseline("complex_user_data", complex_data, create_if_missing=True)
        print("✓ Complex data baseline created/validated successfully")
    except BaselineNotFoundError as e:
        print(f"✓ New baseline created: {e.baseline_path}")
    except BaselineComparisonError as e:
        print(f"✗ Mismatch in complex data: {e}")
    
    # Example 2: List with different data types
    print("\n2. Testing lists with mixed data types...")
    mixed_list_data = {
        "items": [
            {"type": "string", "value": "hello"},
            {"type": "number", "value": 42},
            {"type": "boolean", "value": True},
            {"type": "null", "value": None},
            {"type": "array", "value": [1, 2, 3]},
            {"type": "object", "value": {"nested": "data"}}
        ],
        "summary": {
            "total_items": 6,
            "types_present": ["string", "number", "boolean", "null", "array", "object"]
        }
    }
    
    try:
        generator.test_against_baseline("mixed_types", mixed_list_data, create_if_missing=True)
        print("✓ Mixed types data validated successfully")
    except BaselineNotFoundError as e:
        print(f"✓ Mixed types baseline created: {e.baseline_path}")
    
    # Example 3: Test with list order changes
    print("\n3. Testing list order sensitivity...")
    reordered_data = {
        "items": [
            {"type": "number", "value": 42},      # Moved up
            {"type": "string", "value": "hello"}, # Moved down
            {"type": "boolean", "value": True},
            {"type": "null", "value": None},
            {"type": "array", "value": [1, 2, 3]},
            {"type": "object", "value": {"nested": "data"}}
        ],
        "summary": {
            "total_items": 6,
            "types_present": ["string", "number", "boolean", "null", "array", "object"]
        }
    }
    
    try:
        generator.test_against_baseline("mixed_types", reordered_data)
        print("✓ Reordered data matches baseline")
    except BaselineComparisonError as e:
        print(f"✗ List order matters - differences detected:")
        for diff in e.differences[:3]:  # Show first 3 differences
            print(f"   - {diff}")
        if len(e.differences) > 3:
            print(f"   ... and {len(e.differences) - 3} more differences")
    
    # Example 4: Deep nesting with arrays
    print("\n4. Testing deeply nested structures...")
    deep_nested = {
        "level1": {
            "level2": {
                "level3": {
                    "data": [
                        {
                            "items": [
                                {"id": 1, "values": [10, 20, 30]},
                                {"id": 2, "values": [40, 50, 60]}
                            ]
                        },
                        {
                            "items": [
                                {"id": 3, "values": [70, 80, 90]},
                                {"id": 4, "values": [100, 110, 120]}
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    try:
        generator.test_against_baseline("deep_nested", deep_nested, create_if_missing=True)
        print("✓ Deep nested structure validated successfully")
    except BaselineNotFoundError as e:
        print(f"✓ Deep nested baseline created: {e.baseline_path}")
    
    # Example 5: Test with modification in deep structure
    print("\n5. Testing modification in deep nested structure...")
    modified_deep = {
        "level1": {
            "level2": {
                "level3": {
                    "data": [
                        {
                            "items": [
                                {"id": 1, "values": [10, 20, 30]},
                                {"id": 2, "values": [40, 55, 60]}  # Changed 50 to 55
                            ]
                        },
                        {
                            "items": [
                                {"id": 3, "values": [70, 80, 90]},
                                {"id": 4, "values": [100, 110, 120]}
                            ]
                        }
                    ]
                }
            }
        }
    }
    
    try:
        generator.test_against_baseline("deep_nested", modified_deep)
        print("✓ Modified deep structure matches baseline")
    except BaselineComparisonError as e:
        print(f"✗ Deep modification detected:")
        for diff in e.differences:
            print(f"   - {diff}")
    
    # Example 6: Empty and edge cases
    print("\n6. Testing edge cases...")
    edge_cases = {
        "empty_dict": {},
        "empty_list": [],
        "null_value": None,
        "zero_number": 0,
        "empty_string": "",
        "boolean_false": False,
        "list_with_empties": [None, "", 0, False, {}, []],
        "unicode_strings": ["Hello 世界", "Café ☕", "🚀 Rocket"]
    }
    
    try:
        generator.test_against_baseline("edge_cases", edge_cases, create_if_missing=True)
        print("✓ Edge cases validated successfully")
    except BaselineNotFoundError as e:
        print(f"✓ Edge cases baseline created: {e.baseline_path}")
    
    print("\n=== Complex structures example completed! ===")
    print("This example shows how the baseline generator handles:")
    print("- Nested dictionaries and lists")
    print("- Mixed data types")
    print("- Deep nesting scenarios")
    print("- Edge cases and empty values")
    print("- Precise path reporting for differences")


if __name__ == "__main__":
    main() 