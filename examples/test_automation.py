#!/usr/bin/env python3
"""
Test Automation Example for Baseline Generator

This example demonstrates integrating the baseline generator with pytest
for automated testing scenarios.
"""

import sys
from pathlib import Path
import json

# Add the parent directory to the path so we can import baseline_generator
sys.path.insert(0, str(Path(__file__).parent.parent))

from baseline_generator import BaselineGenerator, BaselineComparisonError, BaselineNotFoundError


class DataProcessor:
    """A sample class that processes data - what we'll be testing."""
    
    def process_user_data(self, raw_data: dict) -> dict:
        """Process raw user data into a standardized format."""
        return {
            "user_id": raw_data.get("id"),
            "full_name": f"{raw_data.get('first_name', '')} {raw_data.get('last_name', '')}".strip(),
            "email": raw_data.get("email", "").lower(),
            "is_verified": raw_data.get("verified", False),
            "account_type": raw_data.get("type", "standard"),
            "metadata": {
                "source": raw_data.get("source", "unknown"),
                "processed_at": "2024-01-15T10:30:00Z",  # Would be datetime.now() in real code
                "version": "1.0"
            }
        }
    
    def aggregate_sales_data(self, sales_records: list) -> dict:
        """Aggregate sales data into summary statistics."""
        if not sales_records:
            return {
                "total_sales": 0,
                "total_revenue": 0.0,
                "average_sale": 0.0,
                "product_breakdown": {},
                "date_range": None
            }
        
        total_sales = len(sales_records)
        total_revenue = sum(record.get("amount", 0) for record in sales_records)
        average_sale = total_revenue / total_sales if total_sales > 0 else 0
        
        # Product breakdown
        product_breakdown = {}
        for record in sales_records:
            product = record.get("product", "unknown")
            if product not in product_breakdown:
                product_breakdown[product] = {"count": 0, "revenue": 0.0}
            product_breakdown[product]["count"] += 1
            product_breakdown[product]["revenue"] += record.get("amount", 0)
        
        # Date range
        dates = [record.get("date") for record in sales_records if record.get("date")]
        date_range = {
            "start": min(dates) if dates else None,
            "end": max(dates) if dates else None
        }
        
        return {
            "total_sales": total_sales,
            "total_revenue": round(total_revenue, 2),
            "average_sale": round(average_sale, 2),
            "product_breakdown": product_breakdown,
            "date_range": date_range
        }


def test_user_data_processing():
    """Test user data processing with baseline comparison."""
    print("=== Test: User Data Processing ===")
    
    generator = BaselineGenerator("examples/test_baselines/automation")
    processor = DataProcessor()
    
    # Test data
    raw_user_data = {
        "id": 12345,
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "ALICE.JOHNSON@EXAMPLE.COM",
        "verified": True,
        "type": "premium",
        "source": "web_signup"
    }
    
    # Process the data
    processed_data = processor.process_user_data(raw_user_data)
    
    try:
        generator.test_against_baseline("processed_user_data", processed_data, create_if_missing=True)
        print("✓ User data processing test passed")
        return True
    except BaselineNotFoundError as e:
        print(f"✓ User processing baseline created: {e.baseline_path}")
        return True
    except BaselineComparisonError as e:
        print(f"✗ User data processing test failed:")
        for diff in e.differences:
            print(f"   - {diff}")
        return False


def test_sales_aggregation():
    """Test sales data aggregation with baseline comparison."""
    print("\n=== Test: Sales Data Aggregation ===")
    
    generator = BaselineGenerator("examples/test_baselines/automation")
    processor = DataProcessor()
    
    # Test data
    sales_records = [
        {"product": "Widget A", "amount": 29.99, "date": "2024-01-10"},
        {"product": "Widget B", "amount": 39.99, "date": "2024-01-11"},
        {"product": "Widget A", "amount": 29.99, "date": "2024-01-12"},
        {"product": "Widget C", "amount": 49.99, "date": "2024-01-13"},
        {"product": "Widget B", "amount": 39.99, "date": "2024-01-14"}
    ]
    
    # Aggregate the data
    aggregated_data = processor.aggregate_sales_data(sales_records)
    
    try:
        generator.test_against_baseline("aggregated_sales_data", aggregated_data, create_if_missing=True)
        print("✓ Sales aggregation test passed")
        return True
    except BaselineNotFoundError as e:
        print(f"✓ Sales aggregation baseline created: {e.baseline_path}")
        return True
    except BaselineComparisonError as e:
        print(f"✗ Sales aggregation test failed:")
        for diff in e.differences:
            print(f"   - {diff}")
        return False


def test_empty_sales_data():
    """Test edge case: empty sales data."""
    print("\n=== Test: Empty Sales Data ===")
    
    generator = BaselineGenerator("examples/test_baselines/automation")
    processor = DataProcessor()
    
    # Test with empty data
    empty_sales = []
    aggregated_empty = processor.aggregate_sales_data(empty_sales)
    
    try:
        generator.test_against_baseline("empty_sales_data", aggregated_empty, create_if_missing=True)
        print("✓ Empty sales data test passed")
        return True
    except BaselineNotFoundError as e:
        print(f"✓ Empty sales baseline created: {e.baseline_path}")
        return True
    except BaselineComparisonError as e:
        print(f"✗ Empty sales data test failed:")
        for diff in e.differences:
            print(f"   - {diff}")
        return False


def test_regression_scenario():
    """Simulate a regression test where the logic changes."""
    print("\n=== Test: Regression Detection ===")
    
    generator = BaselineGenerator("examples/test_baselines/automation")
    processor = DataProcessor()
    
    # Original user data
    user_data = {
        "id": 98765,
        "first_name": "Bob",
        "last_name": "Smith",
        "email": "bob.smith@example.com",
        "verified": False,
        "type": "standard"
    }
    
    processed = processor.process_user_data(user_data)
    
    # First, create/verify the baseline
    try:
        generator.test_against_baseline("user_regression_test", processed, create_if_missing=True)
        print("✓ Regression baseline established")
    except BaselineNotFoundError:
        print("✓ Regression baseline created")
    except BaselineComparisonError:
        print("✗ Unexpected baseline mismatch")
        return False
    
    # Now simulate a change in the processing logic
    # Let's say the developer accidentally changed the email processing
    original_email = processed["email"]
    processed["email"] = processed["email"].upper()  # This would be a bug - emails should be lowercase
    
    try:
        generator.test_against_baseline("user_regression_test", processed)
        print("✗ Regression not detected - this would be a test failure!")
        return False
    except BaselineComparisonError as e:
        print("✓ Regression detected successfully:")
        for diff in e.differences:
            print(f"   - {diff}")
        return True


def run_test_suite():
    """Run all tests and provide a summary."""
    print("=== Baseline Generator Test Automation Example ===\n")
    
    tests = [
        ("User Data Processing", test_user_data_processing),
        ("Sales Data Aggregation", test_sales_aggregation),
        ("Empty Sales Data", test_empty_sales_data),
        ("Regression Detection", test_regression_scenario)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status:4} | {test_name}")
    
    print("-"*50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed - check output above")
    
    print("\n=== Benefits of Using Baseline Generator for Testing ===")
    print("- Automatic regression detection")
    print("- Clear difference reporting")
    print("- Easy baseline creation and management")
    print("- Version control friendly (JSON files)")
    print("- Handles complex nested data structures")
    print("- Integrates well with existing test frameworks")
    
    return passed == total


def pytest_example():
    """Example of how this would look in a pytest test file."""
    example_code = '''
# test_data_processing.py - Example pytest integration

import pytest
from baseline_generator import BaselineGenerator, BaselineComparisonError

@pytest.fixture
def baseline_generator():
    return BaselineGenerator("tests/baselines")

@pytest.fixture
def sample_data():
    return {"user_id": 123, "name": "Test User"}

def test_data_processing_baseline(baseline_generator, sample_data):
    """Test that data processing output matches the established baseline."""
    
    processed_data = process_user_data(sample_data)  # Your function
    
    # This will automatically create baseline on first run
    # and compare against it on subsequent runs
    try:
        baseline_generator.test_against_baseline(
            "processed_user_data", 
            processed_data, 
            create_if_missing=True
        )
    except BaselineComparisonError as e:
        pytest.fail(f"Data processing output changed: {e.differences}")

def test_api_response_baseline(baseline_generator):
    """Test API response format against baseline."""
    
    response = make_api_call("/api/users/123")  # Your API call
    
    try:
        baseline_generator.test_against_baseline(
            "api_user_response", 
            response, 
            create_if_missing=True
        )
    except BaselineComparisonError as e:
        pytest.fail(f"API response format changed: {e.differences}")
'''
    
    print("\n=== Pytest Integration Example ===")
    print(example_code)


if __name__ == "__main__":
    success = run_test_suite()
    pytest_example()
    
    if not success:
        sys.exit(1) 