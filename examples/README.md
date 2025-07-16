# Baseline Generator Examples

This directory contains practical examples demonstrating how to use the Baseline Generator tool in various scenarios. These examples help you understand the capabilities and test the tool manually before integrating it into your projects.

## 📁 Example Files

### 1. `basic_usage.py` - Getting Started
**What it demonstrates:**
- Creating your first baseline
- Testing data against existing baselines
- Handling mismatches and differences
- Auto-creation of missing baselines

**Run it:**
```bash
python examples/basic_usage.py
```

**Key concepts covered:**
- Basic API usage
- Error handling with `BaselineComparisonError`
- Understanding difference reporting
- File management

### 2. `complex_structures.py` - Advanced Data Handling
**What it demonstrates:**
- Nested dictionaries and lists
- Mixed data types
- Deep nesting scenarios
- Edge cases (empty values, unicode)
- Precise path reporting for differences

**Run it:**
```bash
python examples/complex_structures.py
```

**Key concepts covered:**
- Complex data structure comparison
- List order sensitivity
- Deep nesting path tracking
- Edge case handling

### 3. `api_testing.py` - API Response Validation
**What it demonstrates:**
- API response regression testing
- Error response validation
- Contract testing with required fields
- Detecting breaking changes
- Component-specific testing (pagination, etc.)

**Run it:**
```bash
python examples/api_testing.py
```

**Key concepts covered:**
- Real-world API testing scenarios
- Contract vs. full response testing
- Error response handling
- Regression detection

### 4. `test_automation.py` - Test Framework Integration
**What it demonstrates:**
- Integration with test automation
- Regression detection
- Test suite organization
- pytest integration examples

**Run it:**
```bash
python examples/test_automation.py
```

**Key concepts covered:**
- Automated testing workflows
- Test result reporting
- Integration patterns
- Best practices for test automation

## 🚀 Quick Start

1. **Install dependencies** (if not already done):
   ```bash
   cd /path/to/baseline-generator
   poetry install
   ```

2. **Run all examples**:
   ```bash
   # Run examples individually
   python examples/basic_usage.py
   python examples/complex_structures.py
   python examples/api_testing.py
   python examples/test_automation.py
   
   # Or run them all with:
   ./examples/run_all_examples.sh  # (if created)
   ```

3. **Examine generated baselines**:
   After running the examples, check the created baseline files:
   ```bash
   ls -la examples/test_baselines/
   ls -la examples/test_baselines/api/
   ls -la examples/test_baselines/automation/
   ```

## 📊 Generated Test Data

The examples will create several directories with baseline files:

```
examples/test_baselines/
├── user_profile.json              # Basic user data
├── product_info.json              # Product information
├── complex_user_data.json         # Nested user structure
├── mixed_types.json               # Mixed data types
├── deep_nested.json               # Deep nesting example
├── edge_cases.json                # Edge cases and empty values
├── api/
│   ├── user_profile_response.json # API user response
│   ├── posts_listing_response.json# API posts listing
│   ├── post_not_found_error.json  # Error response
│   ├── pagination_structure.json  # Pagination component
│   └── user_contract.json         # API contract
└── automation/
    ├── processed_user_data.json   # Processed user data
    ├── aggregated_sales_data.json # Sales aggregation
    ├── empty_sales_data.json      # Empty data handling
    └── user_regression_test.json  # Regression test baseline
```

## 🎯 Use Cases Demonstrated

### 1. **Data Processing Validation**
- Ensure data transformation functions produce consistent output
- Catch unexpected changes in processing logic
- Validate edge cases and error conditions

### 2. **API Testing**
- Regression testing for API responses
- Contract testing to ensure required fields
- Error response format validation
- Breaking change detection

### 3. **Test Automation**
- Integration with pytest and other frameworks
- Automated regression detection
- Continuous integration workflows
- Test result reporting

### 4. **Complex Data Structures**
- Nested JSON validation
- List ordering verification
- Deep path difference tracking
- Mixed type handling

## 🔧 Customization

### Running with Custom Test Folders
Modify the examples to use your own test folders:

```python
# Instead of:
generator = BaselineGenerator("examples/test_baselines")

# Use:
generator = BaselineGenerator("your/custom/path")
```

### Integration with Your Data
Replace the sample data in examples with your actual data structures:

```python
# Replace sample data
your_data = load_your_actual_data()

# Test against baseline
generator.test_against_baseline("your_baseline", your_data)
```

## 📝 Example Output

When you run the examples, you'll see output like:

```
=== Basic Baseline Generator Usage ===

1. Creating a simple baseline...
✓ Baseline 'user_profile.json' created successfully

2. Testing with matching data...
✓ Data matches baseline perfectly!

3. Testing with modified data...
✗ Expected mismatch detected:
   - name: Value mismatch - baseline: 'John Doe', test: 'Jane Doe'
   - age: Value mismatch - baseline: 30, test: 25
```

## 🔍 Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're running from the project root or the path is set correctly
2. **Permission errors**: Ensure the examples directory is writable
3. **Path issues**: Check that baseline directories are created properly

### Debugging Tips

1. **Examine baseline files**: Look at the generated JSON files to understand the expected format
2. **Check differences**: The error messages show exact paths and mismatched values
3. **Start simple**: Begin with `basic_usage.py` before moving to complex examples

## 📚 Next Steps

After running these examples:

1. **Integrate into your project**: Use the patterns shown to add baseline testing to your codebase
2. **Customize for your needs**: Adapt the examples to your specific data structures and workflows
3. **Add to CI/CD**: Include baseline tests in your continuous integration pipeline
4. **Explore advanced features**: Check the main documentation for additional configuration options

## 🤝 Contributing

If you create additional useful examples:

1. Follow the same pattern as existing examples
2. Include comprehensive documentation
3. Add error handling and clear output messages
4. Test with various data scenarios

---

**Need help?** Check the main project README or open an issue if you encounter problems with any examples. 