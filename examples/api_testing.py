#!/usr/bin/env python3
"""
API Response Testing Example for Baseline Generator

This example demonstrates how to use the baseline generator for:
1. API response validation
2. Regression testing
3. Contract testing
4. Error response validation
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Union

# Add the parent directory to the path so we can import baseline_generator
sys.path.insert(0, str(Path(__file__).parent.parent))

from baseline_generator import BaselineGenerator, BaselineComparisonError, BaselineNotFoundError


def simulate_api_response(endpoint: str, params: Union[dict, None] = None) -> dict:
    """Simulate API responses for testing purposes."""
    
    if endpoint == "/api/users/123":
        return {
            "id": 123,
            "username": "johndoe",
            "email": "john.doe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "profile": {
                "bio": "Software developer",
                "location": "San Francisco, CA",
                "website": "https://johndoe.dev",
                "avatar_url": "https://example.com/avatars/johndoe.jpg"
            },
            "preferences": {
                "email_notifications": True,
                "theme": "dark",
                "language": "en-US"
            },
            "stats": {
                "posts_count": 42,
                "followers_count": 150,
                "following_count": 75
            }
        }
    
    elif endpoint == "/api/posts":
        return {
            "data": [
                {
                    "id": 1,
                    "title": "Getting Started with Python",
                    "slug": "getting-started-with-python",
                    "content": "Python is a great programming language...",
                    "excerpt": "Learn the basics of Python programming",
                    "author": {
                        "id": 123,
                        "username": "johndoe",
                        "display_name": "John Doe"
                    },
                    "published_at": "2024-01-10T14:30:00Z",
                    "updated_at": "2024-01-12T09:15:00Z",
                    "tags": ["python", "programming", "tutorial"],
                    "category": "Programming",
                    "status": "published",
                    "view_count": 1250,
                    "like_count": 89,
                    "comment_count": 12
                },
                {
                    "id": 2,
                    "title": "Advanced Python Concepts",
                    "slug": "advanced-python-concepts",
                    "content": "Dive deeper into Python with these concepts...",
                    "excerpt": "Advanced techniques for Python developers",
                    "author": {
                        "id": 123,
                        "username": "johndoe", 
                        "display_name": "John Doe"
                    },
                    "published_at": "2024-01-14T16:45:00Z",
                    "updated_at": "2024-01-14T16:45:00Z",
                    "tags": ["python", "advanced", "programming"],
                    "category": "Programming",
                    "status": "published",
                    "view_count": 892,
                    "like_count": 67,
                    "comment_count": 8
                }
            ],
            "pagination": {
                "current_page": 1,
                "per_page": 10,
                "total_pages": 5,
                "total_items": 42,
                "has_next": True,
                "has_previous": False
            },
            "meta": {
                "request_id": "req_abc123",
                "response_time_ms": 145,
                "cache_hit": False
            }
        }
    
    elif endpoint == "/api/posts/999":
        # Simulate 404 error
        return {
            "error": {
                "code": "POST_NOT_FOUND",
                "message": "Post with ID 999 was not found",
                "details": {
                    "resource": "post",
                    "id": 999,
                    "suggestions": [
                        "Check if the post ID is correct",
                        "Verify the post exists and is published"
                    ]
                }
            },
            "meta": {
                "request_id": "req_xyz789",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    
    else:
        return {"error": "Unknown endpoint"}


def main():
    print("=== API Response Testing Example ===\n")
    
    # Initialize the generator for API testing
    generator = BaselineGenerator("examples/test_baselines/api")
    
    # Example 1: User profile endpoint
    print("1. Testing user profile API response...")
    user_response = simulate_api_response("/api/users/123")
    
    try:
        generator.test_against_baseline("user_profile_response", user_response, create_if_missing=True)
        print("✓ User profile API response matches baseline")
    except BaselineNotFoundError as e:
        print(f"✓ User profile baseline created: {e.baseline_path}")
    except BaselineComparisonError as e:
        print(f"✗ User profile API changed:")
        for diff in e.differences:
            print(f"   - {diff}")
    
    # Example 2: Posts listing endpoint
    print("\n2. Testing posts listing API response...")
    posts_response = simulate_api_response("/api/posts")
    
    try:
        generator.test_against_baseline("posts_listing_response", posts_response, create_if_missing=True)
        print("✓ Posts listing API response matches baseline")
    except BaselineNotFoundError as e:
        print(f"✓ Posts listing baseline created: {e.baseline_path}")
    except BaselineComparisonError as e:
        print(f"✗ Posts listing API changed:")
        for diff in e.differences[:5]:  # Show first 5 differences
            print(f"   - {diff}")
    
    # Example 3: Test with modified API response (simulating API change)
    print("\n3. Testing API response after backend changes...")
    
    # Simulate a change in the API response
    modified_user_response = simulate_api_response("/api/users/123")
    modified_user_response["profile"]["bio"] = "Senior Software Developer"  # Changed bio
    modified_user_response["stats"]["posts_count"] = 45  # Updated post count
    
    try:
        generator.test_against_baseline("user_profile_response", modified_user_response)
        print("✓ Modified user profile matches baseline")
    except BaselineComparisonError as e:
        print(f"✗ API changes detected (this is expected):")
        for diff in e.differences:
            print(f"   - {diff}")
    
    # Example 4: Error response testing
    print("\n4. Testing error response...")
    error_response = simulate_api_response("/api/posts/999")
    
    try:
        generator.test_against_baseline("post_not_found_error", error_response, create_if_missing=True)
        print("✓ Error response matches baseline")
    except BaselineNotFoundError as e:
        print(f"✓ Error response baseline created: {e.baseline_path}")
    except BaselineComparisonError as e:
        print(f"✗ Error response format changed:")
        for diff in e.differences:
            print(f"   - {diff}")
    
    # Example 5: Testing pagination structure
    print("\n5. Testing pagination structure separately...")
    posts_response = simulate_api_response("/api/posts")
    pagination_only = {"pagination": posts_response["pagination"]}
    
    try:
        generator.test_against_baseline("pagination_structure", pagination_only, create_if_missing=True)
        print("✓ Pagination structure matches baseline")
    except BaselineNotFoundError as e:
        print(f"✓ Pagination baseline created: {e.baseline_path}")
    
    # Example 6: Contract testing - ensure required fields are present
    print("\n6. Testing API contract (required fields)...")
    
    # Create a contract baseline with just the required fields
    user_contract = {
        "id": 123,
        "username": "johndoe",
        "email": "john.doe@example.com",
        "is_active": True,
        "profile": {
            "bio": "Software developer"
        },
        "stats": {
            "posts_count": 42
        }
    }
    
    try:
        generator.test_against_baseline("user_contract", user_contract, create_if_missing=True)
        print("✓ User contract baseline created")
    except BaselineNotFoundError as e:
        print(f"✓ User contract baseline created: {e.baseline_path}")
    
    # Test if the full response satisfies the contract
    try:
        # For contract testing, we'd typically extract only the contract fields
        # from the full response, but here we'll test the full response against
        # the contract to show what would happen with extra fields
        generator.test_against_baseline("user_contract", user_response)
        print("✓ Full response satisfies contract")
    except BaselineComparisonError as e:
        print(f"✗ Contract validation found differences:")
        print(f"   Note: Full API response has {len(e.differences)} extra fields")
        print("   This is normal - contract testing usually checks subset of fields")
    
    print("\n=== API Testing Example Completed! ===")
    print("\nThis example demonstrates:")
    print("- API response regression testing")
    print("- Error response validation")
    print("- Contract testing with required fields")
    print("- Detecting breaking changes in API responses")
    print("- Testing specific components (like pagination)")
    print("\nUse cases:")
    print("- Ensure API responses remain consistent across deployments")
    print("- Catch unintended breaking changes")
    print("- Validate error handling behavior")
    print("- Document expected API response format")


if __name__ == "__main__":
    main() 