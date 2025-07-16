"""Main baseline generator functionality."""

import json
from pathlib import Path
from typing import Any, Union, cast


class BaselineComparisonError(Exception):
    """Raised when baseline comparison fails."""

    def __init__(self, message: str, differences: list[str]) -> None:
        self.message = message
        self.differences = differences
        super().__init__(message)


class BaselineNotFoundError(Exception):
    """Raised when baseline doesn't exist and gets created."""

    def __init__(self, message: str, baseline_path: Path) -> None:
        self.message = message
        self.baseline_path = baseline_path
        super().__init__(message)


class BaselineGenerator:
    """A class for generating and managing test baselines."""

    def __init__(self, test_folder: Union[str, Path] = "tests") -> None:
        """Initialize the BaselineGenerator.

        Args:
            test_folder: Path to the test folder where baselines are stored.
        """
        self.test_folder = Path(test_folder)

    def check_baseline_exists(self, baseline_name: str) -> bool:
        """Check if a baseline file exists in the test folder.

        Args:
            baseline_name: Name of the baseline file (with or without .json extension).

        Returns:
            True if the baseline exists, False otherwise.
        """
        if not baseline_name.endswith(".json"):
            baseline_name += ".json"

        baseline_path = self.test_folder / baseline_name
        return baseline_path.exists()

    def load_baseline(self, baseline_name: str) -> dict[str, Any]:
        """Load a baseline from the test folder.

        Args:
            baseline_name: Name of the baseline file.

        Returns:
            The loaded baseline data.

        Raises:
            FileNotFoundError: If the baseline file doesn't exist.
            json.JSONDecodeError: If the baseline file is not valid JSON.
        """
        if not baseline_name.endswith(".json"):
            baseline_name += ".json"

        baseline_path = self.test_folder / baseline_name

        if not baseline_path.exists():
            raise FileNotFoundError(
                f"Baseline '{baseline_name}' not found in {self.test_folder}"
            )

        with open(baseline_path, "r", encoding="utf-8") as f:
            return cast(dict[str, Any], json.load(f))

    def generate_baseline(
        self, baseline_name: str, data: dict[str, Any], overwrite: bool = False
    ) -> None:
        """Generate a new baseline file.

        Args:
            baseline_name: Name of the baseline file to create.
            data: The data to store in the baseline.
            overwrite: Whether to overwrite existing baseline files.

        Raises:
            FileExistsError: If the baseline already exists and overwrite is False.
        """
        if not baseline_name.endswith(".json"):
            baseline_name += ".json"

        baseline_path = self.test_folder / baseline_name

        if baseline_path.exists() and not overwrite:
            raise FileExistsError(
                f"Baseline '{baseline_name}' already exists. Use overwrite=True to replace it."
            )

        # Create the test folder if it doesn't exist
        self.test_folder.mkdir(parents=True, exist_ok=True)

        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def test_against_baseline(
        self,
        baseline_name: str,
        test_data: dict[str, Any],
        create_if_missing: bool = False,
    ) -> None:
        """Test data against an existing baseline.

        Args:
            baseline_name: Name of the baseline file to compare against.
            test_data: The test data to compare with the baseline.
            create_if_missing: Whether to create the baseline if it doesn't exist.

        Raises:
            BaselineNotFoundError: If baseline doesn't exist and gets created.
            BaselineComparisonError: If the data doesn't match the baseline.
            FileNotFoundError: If baseline doesn't exist and create_if_missing is False.
        """
        if not baseline_name.endswith(".json"):
            baseline_name += ".json"

        baseline_path = self.test_folder / baseline_name

        # Handle missing baseline
        if not baseline_path.exists():
            if create_if_missing:
                self.generate_baseline(baseline_name, test_data, overwrite=False)
                raise BaselineNotFoundError(
                    f"Baseline '{baseline_name}' did not exist and was created. "
                    f"Please review the generated baseline at {baseline_path}",
                    baseline_path,
                )
            else:
                raise BaselineNotFoundError(
                    f"Baseline '{baseline_name}' not found in {self.test_folder}"
                )

        # Load existing baseline and compare
        baseline_data = self.load_baseline(baseline_name)
        differences = self._compare_data(baseline_data, test_data)

        if differences:
            raise BaselineComparisonError(
                f"Test data does not match baseline '{baseline_name}'", differences
            )

    def _compare_data(
        self, baseline: dict[str, Any], test_data: dict[str, Any]
    ) -> list[str]:
        """Compare two data structures and return list of differences.

        Args:
            baseline: The baseline data.
            test_data: The test data to compare.

        Returns:
            List of difference descriptions.
        """
        differences: list[str] = []
        self._compare_recursive(baseline, test_data, "", differences)
        return differences

    def _compare_recursive(
        self, baseline: Any, test_data: Any, path: str, differences: list[str]
    ) -> None:
        """Recursively compare data structures.

        Args:
            baseline: Baseline value at current path.
            test_data: Test value at current path.
            path: Current path in the data structure.
            differences: List to append differences to.
        """
        current_path = path if path else "root"

        if self._check_type_mismatch(baseline, test_data, current_path, differences):
            return

        if isinstance(baseline, dict):
            self._compare_dictionaries(baseline, test_data, path, differences)
        elif isinstance(baseline, list):
            self._compare_lists(baseline, test_data, path, differences)
        else:
            self._compare_primitives(baseline, test_data, current_path, differences)

    def _check_type_mismatch(
        self, baseline: Any, test_data: Any, current_path: str, differences: list[str]
    ) -> bool:
        """Check if baseline and test data have different types.

        Args:
            baseline: Baseline value.
            test_data: Test value.
            current_path: Current path in the data structure.
            differences: List to append differences to.

        Returns:
            True if there's a type mismatch, False otherwise.
        """
        if type(baseline) is not type(test_data):
            differences.append(
                f"{current_path}: Type mismatch - baseline: {type(baseline).__name__}, "
                f"test: {type(test_data).__name__}"
            )
            return True
        return False

    def _compare_dictionaries(
        self,
        baseline: dict[str, Any],
        test_data: dict[str, Any],
        path: str,
        differences: list[str],
    ) -> None:
        """Compare two dictionaries for differences.

        Args:
            baseline: Baseline dictionary.
            test_data: Test dictionary.
            path: Current path in the data structure.
            differences: List to append differences to.
        """
        self._check_missing_keys_in_test_data(baseline, test_data, path, differences)
        self._check_extra_keys_in_test_data(baseline, test_data, path, differences)

    def _check_missing_keys_in_test_data(
        self,
        baseline: dict[str, Any],
        test_data: dict[str, Any],
        path: str,
        differences: list[str],
    ) -> None:
        """Check for keys present in baseline but missing in test data.

        Args:
            baseline: Baseline dictionary.
            test_data: Test dictionary.
            path: Current path in the data structure.
            differences: List to append differences to.
        """
        for key in baseline:
            if key not in test_data:
                new_path = f"{path}.{key}" if path else key
                differences.append(f"{new_path}: Missing in test data")
            else:
                new_path = f"{path}.{key}" if path else key
                self._compare_recursive(
                    baseline[key], test_data[key], new_path, differences
                )

    def _check_extra_keys_in_test_data(
        self,
        baseline: dict[str, Any],
        test_data: dict[str, Any],
        path: str,
        differences: list[str],
    ) -> None:
        """Check for keys present in test data but missing in baseline.

        Args:
            baseline: Baseline dictionary.
            test_data: Test dictionary.
            path: Current path in the data structure.
            differences: List to append differences to.
        """
        for key in test_data:
            if key not in baseline:
                new_path = f"{path}.{key}" if path else key
                differences.append(f"{new_path}: Extra key in test data")

    def _compare_lists(
        self,
        baseline: list[Any],
        test_data: list[Any],
        path: str,
        differences: list[str],
    ) -> None:
        """Compare two lists for differences.

        Args:
            baseline: Baseline list.
            test_data: Test list.
            path: Current path in the data structure.
            differences: List to append differences to.
        """
        if self._check_list_length_mismatch(baseline, test_data, path, differences):
            # Still compare overlapping elements
            min_len = min(len(baseline), len(test_data))
            self._compare_list_elements(baseline, test_data, path, differences, min_len)
        else:
            self._compare_list_elements(
                baseline, test_data, path, differences, len(baseline)
            )

    def _check_list_length_mismatch(
        self,
        baseline: list[Any],
        test_data: list[Any],
        path: str,
        differences: list[str],
    ) -> bool:
        """Check if baseline and test lists have different lengths.

        Args:
            baseline: Baseline list.
            test_data: Test list.
            path: Current path in the data structure.
            differences: List to append differences to.

        Returns:
            True if there's a length mismatch, False otherwise.
        """
        current_path = path if path else "root"
        if len(baseline) != len(test_data):
            differences.append(
                f"{current_path}: List length mismatch - baseline: {len(baseline)}, "
                f"test: {len(test_data)}"
            )
            return True
        return False

    def _compare_list_elements(
        self,
        baseline: list[Any],
        test_data: list[Any],
        path: str,
        differences: list[str],
        length: int,
    ) -> None:
        """Compare elements of two lists up to the specified length.

        Args:
            baseline: Baseline list.
            test_data: Test list.
            path: Current path in the data structure.
            differences: List to append differences to.
            length: Number of elements to compare.
        """
        for i in range(length):
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            self._compare_recursive(baseline[i], test_data[i], new_path, differences)

    def _compare_primitives(
        self, baseline: Any, test_data: Any, current_path: str, differences: list[str]
    ) -> None:
        """Compare two primitive values for differences.

        Args:
            baseline: Baseline primitive value.
            test_data: Test primitive value.
            current_path: Current path in the data structure.
            differences: List to append differences to.
        """
        if baseline != test_data:
            differences.append(
                f"{current_path}: Value mismatch - baseline: {baseline!r}, test: {test_data!r}"
            )
