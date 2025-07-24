"""Main baseline generator functionality."""

import difflib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Union, cast


class Colors:
    """ANSI color codes for terminal output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

    # Class variable to track if colors should be used
    _colors_enabled = None

    @classmethod
    def _detect_color_support(cls) -> bool:
        """Detect if the terminal supports colors."""
        # Check if we're in a terminal
        if not sys.stdout.isatty():
            return False

        # Check environment variables
        if os.environ.get("NO_COLOR"):
            return False

        if os.environ.get("FORCE_COLOR"):
            return True

        # Check TERM environment variable
        term = os.environ.get("TERM", "")
        if term == "dumb":
            return False

        # Most modern terminals support colors
        if any(
            term.startswith(prefix) for prefix in ["xterm", "screen", "tmux", "rxvt"]
        ):
            return True

        # Check for common terminal emulators
        if any(var in os.environ for var in ["COLORTERM", "TERM_PROGRAM"]):
            return True

        # Default to no colors for safety
        return False

    @classmethod
    def colors_enabled(cls) -> bool:
        """Check if colors are enabled."""
        if cls._colors_enabled is None:
            cls._colors_enabled = cls._detect_color_support()
        return cls._colors_enabled

    @classmethod
    def set_colors_enabled(cls, enabled: bool) -> None:
        """Manually set whether colors are enabled."""
        cls._colors_enabled = enabled

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Add color to text if colors are enabled."""
        if cls.colors_enabled():
            return f"{color}{text}{cls.RESET}"
        else:
            return text


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

    def __init__(
        self, test_folder: Union[str, Path] = "tests", colors: bool = None
    ) -> None:
        """Initialize the BaselineGenerator.

        Args:
            test_folder: Path to the test folder where baselines are stored.
            colors: Whether to use colors in output. If None, auto-detect.
        """
        self.test_folder = Path(test_folder)
        if colors is not None:
            Colors.set_colors_enabled(colors)

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
                    f"Baseline '{baseline_name}' not found in {self.test_folder}", 
                    baseline_path,
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
            # For strings, create a detailed diff if they're long
            if isinstance(baseline, str) and isinstance(test_data, str):
                diff_output = self._create_string_diff(
                    baseline, test_data, current_path
                )
                differences.append(diff_output)
            else:
                differences.append(
                    f"{current_path}: Value mismatch - baseline: {baseline!r}, test: {test_data!r}"
                )

    def _create_string_diff(self, baseline: str, test_data: str, path: str) -> str:
        """Create a detailed diff for string values.

        Args:
            baseline: Baseline string value.
            test_data: Test string value.
            path: Current path in the data structure.

        Returns:
            Formatted diff output with colors and context.
        """
        # For very short strings, use simple comparison with character highlighting
        if len(baseline) < 100 and len(test_data) < 100:
            return self._create_simple_string_diff(baseline, test_data, path)

        # For longer strings, try line-by-line diff first
        baseline_lines = baseline.splitlines(keepends=True)
        test_lines = test_data.splitlines(keepends=True)

        # Generate unified diff
        diff_lines = list(
            difflib.unified_diff(
                baseline_lines,
                test_lines,
                fromfile="baseline",
                tofile="test",
                lineterm="",
                n=3,  # Show 3 lines of context
            )
        )

        if not diff_lines:
            # If no line-by-line diff, show character-by-character diff
            return self._create_character_diff(baseline, test_data, path)

        # Enhanced: Also show character-level diff for small changes
        if len(diff_lines) <= 10:  # If the diff is small, also show character-level
            char_diff = self._create_character_diff(baseline, test_data, path)
            line_diff = self._colorize_unified_diff(
                diff_lines, baseline_lines, test_lines
            )
            return (
                f"{path}: String content differs:\n"
                f"{line_diff}\n"
                f"  {Colors.colorize('Summary:', Colors.YELLOW)} "
                f"Baseline: {len(baseline_lines)} lines, Test: {len(test_lines)} lines\n\n"
                f"{Colors.colorize('Character-level view:', Colors.CYAN)}\n{char_diff}"
            )

        # For large diffs, just show the line-by-line diff
        line_diff = self._colorize_unified_diff(diff_lines, baseline_lines, test_lines)
        return (
            f"{path}: String content differs:\n"
            f"{line_diff}\n"
            f"  {Colors.colorize('Summary:', Colors.YELLOW)} "
            f"Baseline: {len(baseline_lines)} lines, Test: {len(test_lines)} lines"
        )

    def _create_simple_string_diff(
        self, baseline: str, test_data: str, path: str
    ) -> str:
        """Create a simple diff for short strings with character highlighting."""
        # Find the differing parts
        first_diff = 0
        while (
            first_diff < len(baseline)
            and first_diff < len(test_data)
            and baseline[first_diff] == test_data[first_diff]
        ):
            first_diff += 1

        if first_diff == len(baseline) and first_diff == len(test_data):
            # Strings are identical (shouldn't happen, but just in case)
            return f"{path}: Strings are identical"

        # Find the last differing position
        last_diff_baseline = len(baseline) - 1
        last_diff_test = len(test_data) - 1

        while (
            last_diff_baseline >= first_diff
            and last_diff_test >= first_diff
            and baseline[last_diff_baseline] == test_data[last_diff_test]
        ):
            last_diff_baseline -= 1
            last_diff_test -= 1

        # Create highlighted versions
        baseline_before = baseline[:first_diff]
        baseline_diff = (
            baseline[first_diff : last_diff_baseline + 1]
            if first_diff <= last_diff_baseline
            else ""
        )
        baseline_after = (
            baseline[last_diff_baseline + 1 :]
            if last_diff_baseline + 1 < len(baseline)
            else ""
        )

        test_before = test_data[:first_diff]
        test_diff = (
            test_data[first_diff : last_diff_test + 1]
            if first_diff <= last_diff_test
            else ""
        )
        test_after = (
            test_data[last_diff_test + 1 :]
            if last_diff_test + 1 < len(test_data)
            else ""
        )

        if Colors.colors_enabled():
            highlighted_baseline = (
                baseline_before
                + Colors.colorize(baseline_diff, Colors.RED + Colors.BOLD)
                + baseline_after
            )

            highlighted_test = (
                test_before
                + Colors.colorize(test_diff, Colors.GREEN + Colors.BOLD)
                + test_after
            )

            # For colored output, we need to show the strings clearly
            # Add quotes around the content but don't use repr()
            baseline_display = f"'{highlighted_baseline}'"
            test_display = f"'{highlighted_test}'"
        else:
            # Use brackets and markers for non-color terminals
            highlighted_baseline = (
                baseline_before + f"<<<{baseline_diff}>>>" + baseline_after
            )
            highlighted_test = test_before + f"<<<{test_diff}>>>" + test_after

            # For non-colored output, use repr() to show special characters
            baseline_display = repr(highlighted_baseline)
            test_display = repr(highlighted_test)

        baseline_label = (
            Colors.colorize("- Baseline:", Colors.RED)
            if Colors.colors_enabled()
            else "- Baseline:"
        )
        test_label = (
            Colors.colorize("+ Test:", Colors.GREEN)
            if Colors.colors_enabled()
            else "+ Test:"
        )

        return (
            f"{path}: String mismatch:\n"
            f"  {baseline_label} {baseline_display}\n"
            f"  {test_label}     {test_display}"
        )

    def _colorize_unified_diff(
        self, diff_lines: list[str], baseline_lines: list[str], test_lines: list[str]
    ) -> str:
        """Colorize the unified diff output."""
        if not Colors.colors_enabled():
            # Return plain diff when colors are disabled
            return "\n".join(diff_lines)

        colored_diff = []
        for line in diff_lines:
            if line.startswith("---") or line.startswith("+++"):
                colored_diff.append(Colors.colorize(line, Colors.BOLD))
            elif line.startswith("@@"):
                colored_diff.append(Colors.colorize(line, Colors.CYAN))
            elif line.startswith("-"):
                colored_diff.append(Colors.colorize(line, Colors.RED))
            elif line.startswith("+"):
                colored_diff.append(Colors.colorize(line, Colors.GREEN))
            else:
                colored_diff.append(line)

        return "\n".join(colored_diff)

    def _create_character_diff(self, baseline: str, test_data: str, path: str) -> str:
        """Create a character-by-character diff for strings without line breaks.

        Args:
            baseline: Baseline string value.
            test_data: Test string value.
            path: Current path in the data structure.

        Returns:
            Formatted character diff output.
        """
        # Find the first and last differing positions
        first_diff = 0
        while (
            first_diff < len(baseline)
            and first_diff < len(test_data)
            and baseline[first_diff] == test_data[first_diff]
        ):
            first_diff += 1

        last_diff_baseline = len(baseline) - 1
        last_diff_test = len(test_data) - 1

        while (
            last_diff_baseline >= first_diff
            and last_diff_test >= first_diff
            and baseline[last_diff_baseline] == test_data[last_diff_test]
        ):
            last_diff_baseline -= 1
            last_diff_test -= 1

        # Show context around the difference
        context_size = 50
        start_baseline = max(0, first_diff - context_size)
        end_baseline = min(len(baseline), last_diff_baseline + context_size + 1)
        start_test = max(0, first_diff - context_size)
        end_test = min(len(test_data), last_diff_test + context_size + 1)

        baseline_context = baseline[start_baseline:end_baseline]
        test_context = test_data[start_test:end_test]

        # Highlight the different parts within the context
        if first_diff < len(baseline):
            diff_start_in_context = first_diff - start_baseline
            diff_end_in_context = last_diff_baseline + 1 - start_baseline

            baseline_before = baseline_context[:diff_start_in_context]
            baseline_diff = baseline_context[diff_start_in_context:diff_end_in_context]
            baseline_after = baseline_context[diff_end_in_context:]

            if Colors.colors_enabled():
                highlighted_baseline = (
                    baseline_before
                    + Colors.colorize(baseline_diff, Colors.RED + Colors.BOLD)
                    + baseline_after
                )
            else:
                highlighted_baseline = (
                    baseline_before + f"<<<{baseline_diff}>>>" + baseline_after
                )
        else:
            highlighted_baseline = baseline_context

        if first_diff < len(test_data):
            diff_start_in_context = first_diff - start_test
            diff_end_in_context = last_diff_test + 1 - start_test

            test_before = test_context[:diff_start_in_context]
            test_diff = test_context[diff_start_in_context:diff_end_in_context]
            test_after = test_context[diff_end_in_context:]

            if Colors.colors_enabled():
                highlighted_test = (
                    test_before
                    + Colors.colorize(test_diff, Colors.GREEN + Colors.BOLD)
                    + test_after
                )
            else:
                highlighted_test = test_before + f"<<<{test_diff}>>>" + test_after
        else:
            highlighted_test = test_context

        # Add ellipsis if content is truncated
        baseline_prefix = "..." if start_baseline > 0 else ""
        baseline_suffix = "..." if end_baseline < len(baseline) else ""
        test_prefix = "..." if start_test > 0 else ""
        test_suffix = "..." if end_test < len(test_data) else ""

        baseline_label = (
            Colors.colorize("- Baseline:", Colors.RED)
            if Colors.colors_enabled()
            else "- Baseline:"
        )
        test_label = (
            Colors.colorize("+ Test:", Colors.GREEN)
            if Colors.colors_enabled()
            else "+ Test:"
        )
        info_label = (
            Colors.colorize("Info:", Colors.YELLOW)
            if Colors.colors_enabled()
            else "Info:"
        )

        return (
            f"{path}: String differs at position {first_diff}:\n"
            f"  {baseline_label} {baseline_prefix}{highlighted_baseline}{baseline_suffix}\n"
            f"  {test_label}     {test_prefix}{highlighted_test}{test_suffix}\n"
            f"  {info_label} "
            f"Baseline length: {len(baseline)}, Test length: {len(test_data)}"
        )
