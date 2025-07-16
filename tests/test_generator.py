"""Tests for the BaselineGenerator class."""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict

import pytest

from baseline_generator import (
    BaselineComparisonError,
    BaselineGenerator,
    BaselineNotFoundError,
)


class TestBaselineGenerator:
    """Test cases for BaselineGenerator."""

    def test_init_with_default_folder(self) -> None:
        """Test initialization with default test folder."""
        generator = BaselineGenerator()
        assert generator.test_folder == Path("tests")

    def test_init_with_custom_folder(self) -> None:
        """Test initialization with custom test folder."""
        custom_folder = "custom_tests"
        generator = BaselineGenerator(custom_folder)
        assert generator.test_folder == Path(custom_folder)

    def test_init_with_path_object(self) -> None:
        """Test initialization with Path object."""
        custom_path = Path("custom_tests")
        generator = BaselineGenerator(custom_path)
        assert generator.test_folder == custom_path

    def test_check_baseline_exists_false(self) -> None:
        """Test checking for non-existent baseline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            assert not generator.check_baseline_exists("nonexistent")

    def test_check_baseline_exists_true(self) -> None:
        """Test checking for existing baseline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline_file = temp_path / "test_baseline.json"
            baseline_file.write_text('{"test": "data"}')

            generator = BaselineGenerator(temp_dir)
            assert generator.check_baseline_exists("test_baseline")
            assert generator.check_baseline_exists("test_baseline.json")

    def test_load_baseline_success(self) -> None:
        """Test loading an existing baseline."""
        test_data = {"key": "value", "number": 42}

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline_file = temp_path / "test_baseline.json"
            baseline_file.write_text(json.dumps(test_data))

            generator = BaselineGenerator(temp_dir)
            loaded_data = generator.load_baseline("test_baseline")
            assert loaded_data == test_data

    def test_load_baseline_not_found(self) -> None:
        """Test loading a non-existent baseline."""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)

            with pytest.raises(
                FileNotFoundError, match="Baseline 'nonexistent.json' not found"
            ):
                generator.load_baseline("nonexistent")

    def test_generate_baseline_success(self) -> None:
        """Test generating a new baseline."""
        test_data = {"test": "data", "values": [1, 2, 3]}

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("new_baseline", test_data)

            # Verify the file was created
            baseline_path = Path(temp_dir) / "new_baseline.json"
            assert baseline_path.exists()

            # Verify the content
            with open(baseline_path, "r") as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data

    def test_generate_baseline_already_exists(self) -> None:
        """Test generating a baseline that already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline_file = temp_path / "existing.json"
            baseline_file.write_text('{"old": "data"}')

            generator = BaselineGenerator(temp_dir)

            with pytest.raises(
                FileExistsError, match="Baseline 'existing.json' already exists"
            ):
                generator.generate_baseline("existing", {"new": "data"})

    def test_generate_baseline_overwrite(self) -> None:
        """Test overwriting an existing baseline."""
        old_data = {"old": "data"}
        new_data = {"new": "data"}

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline_file = temp_path / "existing.json"
            baseline_file.write_text(json.dumps(old_data))

            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("existing", new_data, overwrite=True)

            # Verify the content was updated
            with open(baseline_file, "r") as f:
                loaded_data = json.load(f)
            assert loaded_data == new_data

    def test_generate_baseline_creates_directory(self) -> None:
        """Test that generate_baseline creates the test directory if it doesn't exist."""
        test_data = {"test": "data"}

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "test_folder"
            generator = BaselineGenerator(nested_path)

            # Directory shouldn't exist initially
            assert not nested_path.exists()

            generator.generate_baseline("test", test_data)

            # Directory should be created
            assert nested_path.exists()
            baseline_file = nested_path / "test.json"
            assert baseline_file.exists()


class TestBaselineComparison:
    """Test cases for baseline comparison functionality."""

    def test_test_against_baseline_matching_data(self) -> None:
        """Test successful comparison with matching data."""
        baseline_data = {
            "key": "value",
            "numbers": [1, 2, 3],
            "nested": {"inner": True},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("test_baseline", baseline_data)

            # Should not raise any exception
            generator.test_against_baseline("test_baseline", baseline_data)

    def test_test_against_baseline_missing_creates_baseline(self) -> None:
        """Test that missing baseline gets created and raises BaselineNotFoundError."""
        test_data = {"test": "data"}

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            baseline_path = Path(temp_dir) / "new_baseline.json"

            # Should raise BaselineNotFoundError and create the baseline
            with pytest.raises(BaselineNotFoundError) as exc_info:
                generator.test_against_baseline("new_baseline", test_data)

            assert "did not exist and was created" in str(exc_info.value)
            assert exc_info.value.baseline_path == baseline_path
            assert baseline_path.exists()

            # Verify the content
            with open(baseline_path, "r") as f:
                created_data = json.load(f)
            assert created_data == test_data

    def test_test_against_baseline_missing_no_create(self) -> None:
        """Test behavior when baseline is missing and create_if_missing is False."""
        test_data = {"test": "data"}

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)

            with pytest.raises(FileNotFoundError, match="not found"):
                generator.test_against_baseline(
                    "missing_baseline", test_data, create_if_missing=False
                )

    def test_test_against_baseline_value_mismatch(self) -> None:
        """Test comparison failure with value mismatches."""
        baseline_data = {"key": "value", "number": 42}
        test_data = {"key": "different_value", "number": 99}

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("test_baseline", baseline_data)

            with pytest.raises(BaselineComparisonError) as exc_info:
                generator.test_against_baseline("test_baseline", test_data)

            differences = exc_info.value.differences
            assert len(differences) == 2
            assert any("key: Value mismatch" in diff for diff in differences)
            assert any("number: Value mismatch" in diff for diff in differences)

    def test_test_against_baseline_missing_keys(self) -> None:
        """Test comparison failure with missing keys."""
        baseline_data = {"key1": "value1", "key2": "value2", "key3": "value3"}
        test_data = {"key1": "value1", "key3": "value3"}  # missing key2

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("test_baseline", baseline_data)

            with pytest.raises(BaselineComparisonError) as exc_info:
                generator.test_against_baseline("test_baseline", test_data)

            differences = exc_info.value.differences
            assert len(differences) == 1
            assert "key2: Missing in test data" in differences[0]

    def test_test_against_baseline_extra_keys(self) -> None:
        """Test comparison failure with extra keys."""
        baseline_data = {"key1": "value1"}
        test_data = {"key1": "value1", "extra_key": "extra_value"}

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("test_baseline", baseline_data)

            with pytest.raises(BaselineComparisonError) as exc_info:
                generator.test_against_baseline("test_baseline", test_data)

            differences = exc_info.value.differences
            assert len(differences) == 1
            assert "extra_key: Extra key in test data" in differences[0]

    def test_test_against_baseline_type_mismatch(self) -> None:
        """Test comparison failure with type mismatches."""
        baseline_data = {"value": "string", "number": 42}
        test_data = {"value": 123, "number": "42"}  # type mismatches

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("test_baseline", baseline_data)

            with pytest.raises(BaselineComparisonError) as exc_info:
                generator.test_against_baseline("test_baseline", test_data)

            differences = exc_info.value.differences
            assert len(differences) == 2
            assert any("value: Type mismatch" in diff for diff in differences)
            assert any("number: Type mismatch" in diff for diff in differences)

    def test_test_against_baseline_nested_structure_differences(self) -> None:
        """Test comparison with differences in nested structures."""
        baseline_data = {
            "nested": {"inner1": {"value": 1}, "inner2": {"list": [1, 2, 3]}}
        }
        test_data = {
            "nested": {
                "inner1": {"value": 2},  # different value
                "inner2": {"list": [1, 2, 3, 4]},  # different list length
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("test_baseline", baseline_data)

            with pytest.raises(BaselineComparisonError) as exc_info:
                generator.test_against_baseline("test_baseline", test_data)

            differences = exc_info.value.differences
            assert len(differences) == 2
            assert any(
                "nested.inner1.value: Value mismatch" in diff for diff in differences
            )
            assert any(
                "nested.inner2.list: List length mismatch" in diff
                for diff in differences
            )

    def test_test_against_baseline_list_differences(self) -> None:
        """Test comparison with list differences."""
        baseline_data = {"list": [1, "two", {"three": 3}]}
        test_data = {"list": [1, "TWO", {"three": 4}]}  # different values

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("test_baseline", baseline_data)

            with pytest.raises(BaselineComparisonError) as exc_info:
                generator.test_against_baseline("test_baseline", test_data)

            differences = exc_info.value.differences
            assert len(differences) == 2
            assert any("list[1]: Value mismatch" in diff for diff in differences)
            assert any("list[2].three: Value mismatch" in diff for diff in differences)

    def test_test_against_baseline_complex_nested_path(self) -> None:
        """Test that difference paths are correctly formatted for complex nested structures."""
        baseline_data = {"level1": {"level2": [{"level3": {"level4": "value"}}]}}
        test_data = {"level1": {"level2": [{"level3": {"level4": "different"}}]}}

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = BaselineGenerator(temp_dir)
            generator.generate_baseline("test_baseline", baseline_data)

            with pytest.raises(BaselineComparisonError) as exc_info:
                generator.test_against_baseline("test_baseline", test_data)

            differences = exc_info.value.differences
            assert len(differences) == 1
            assert "level1.level2[0].level3.level4: Value mismatch" in differences[0]
