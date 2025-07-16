#!/usr/bin/env python3
"""
Run All Examples Script

This script runs all baseline generator examples in sequence and provides
a summary of the results. Useful for comprehensive testing.
"""

import sys
import subprocess
from pathlib import Path
import time


def run_example(script_name: str) -> tuple[bool, str, float]:
    """Run a single example script and return success status, output, and duration."""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        return False, f"Script {script_name} not found", 0.0
    
    try:
        start_time = time.time()
        # Use poetry run to avoid sandboxing issues
        result = subprocess.run(
            ["poetry", "run", "python", str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout
            cwd=Path(__file__).parent.parent  # Run from project root
        )
        duration = time.time() - start_time
        
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        
        return success, output, duration
        
    except subprocess.TimeoutExpired:
        return False, "Script timed out after 60 seconds", 60.0
    except Exception as e:
        return False, f"Failed to run script: {e}", 0.0


def main():
    """Run all examples and provide a summary."""
    print("=" * 60)
    print("🚀 RUNNING ALL BASELINE GENERATOR EXAMPLES")
    print("=" * 60)
    print()
    
    examples = [
        ("basic_usage.py", "Basic Usage - Getting Started"),
        ("complex_structures.py", "Complex Data Structures"),
        ("api_testing.py", "API Response Validation"),
        ("test_automation.py", "Test Automation Integration")
    ]
    
    results = []
    total_duration = 0.0
    
    for script_name, description in examples:
        print(f"📋 Running: {description}")
        print(f"   Script: {script_name}")
        print("   " + "-" * 50)
        
        success, output, duration = run_example(script_name)
        total_duration += duration
        
        if success:
            print(f"   ✅ SUCCESS ({duration:.2f}s)")
            # Show first few lines of output for context
            lines = output.strip().split('\n')
            if len(lines) > 3:
                for line in lines[:3]:
                    print(f"   {line}")
                if len(lines) > 3:
                    print(f"   ... ({len(lines) - 3} more lines)")
            else:
                for line in lines:
                    print(f"   {line}")
        else:
            print(f"   ❌ FAILED ({duration:.2f}s)")
            print(f"   Error: {output}")
        
        print()
        results.append((script_name, description, success, duration))
    
    # Summary
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    successful = sum(1 for _, _, success, _ in results if success)
    total = len(results)
    
    print(f"Total examples: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Total duration: {total_duration:.2f}s")
    print()
    
    # Detailed results
    print("Detailed Results:")
    print("-" * 60)
    for script_name, description, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {description:30} | {duration:6.2f}s | {script_name}")
    
    print()
    
    if successful == total:
        print("🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print()
        print("Next steps:")
        print("1. Check the generated baseline files in examples/test_baselines/")
        print("2. Examine the baseline JSON files to understand the data format")
        print("3. Try modifying the example data and re-running to see difference detection")
        print("4. Integrate the baseline generator into your own projects")
    else:
        print("⚠️  SOME EXAMPLES FAILED")
        print()
        print("Troubleshooting:")
        print("1. Check the error messages above")
        print("2. Ensure all dependencies are installed (poetry install)")
        print("3. Verify Python version compatibility (3.12+)")
        print("4. Check file permissions for the examples directory")
        
        return False
    
    print()
    print("📁 Generated Files:")
    print("Check these directories for the created baseline files:")
    print("- examples/test_baselines/")
    print("- examples/test_baselines/api/")
    print("- examples/test_baselines/automation/")
    print()
    print("🔍 To examine the baseline files:")
    print("ls -la examples/test_baselines/")
    print("cat examples/test_baselines/user_profile.json")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 