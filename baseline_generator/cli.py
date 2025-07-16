"""Command-line interface for baseline generator."""

import argparse
import json
import sys
from pathlib import Path

from .generator import BaselineComparisonError, BaselineGenerator, BaselineNotFoundError


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Baseline Generator - Generate and manage test baselines"
    )
    parser.add_argument(
        "--test-folder",
        "-t",
        type=str,
        default="tests",
        help="Path to the test folder (default: tests)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check if a baseline exists")
    check_parser.add_argument("baseline_name", help="Name of the baseline to check")

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate a new baseline")
    generate_parser.add_argument("baseline_name", help="Name of the baseline to create")
    generate_parser.add_argument(
        "data_file", help="JSON file containing the baseline data"
    )
    generate_parser.add_argument(
        "--overwrite", "-o", action="store_true", help="Overwrite existing baseline"
    )

    # Load command
    load_parser = subparsers.add_parser("load", help="Load and display a baseline")
    load_parser.add_argument("baseline_name", help="Name of the baseline to load")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test data against a baseline")
    test_parser.add_argument(
        "baseline_name", help="Name of the baseline to test against"
    )
    test_parser.add_argument("data_file", help="JSON file containing the test data")
    test_parser.add_argument(
        "--no-create",
        action="store_true",
        help="Don't create baseline if it doesn't exist (fail instead)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    generator = BaselineGenerator(args.test_folder)

    try:
        if args.command == "check":
            exists = generator.check_baseline_exists(args.baseline_name)
            if exists:
                print(f"✓ Baseline '{args.baseline_name}' exists in {args.test_folder}")
            else:
                print(
                    f"✗ Baseline '{args.baseline_name}' not found in {args.test_folder}"
                )
                sys.exit(1)

        elif args.command == "generate":
            # Load data from file
            data_path = Path(args.data_file)
            if not data_path.exists():
                print(f"Error: Data file '{args.data_file}' not found")
                sys.exit(1)

            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in '{args.data_file}': {e}")
                sys.exit(1)

            generator.generate_baseline(
                args.baseline_name, data, overwrite=args.overwrite
            )
            print(f"✓ Generated baseline '{args.baseline_name}' in {args.test_folder}")

        elif args.command == "load":
            data = generator.load_baseline(args.baseline_name)
            print(json.dumps(data, indent=2, ensure_ascii=False))

        elif args.command == "test":
            # Load test data from file
            data_path = Path(args.data_file)
            if not data_path.exists():
                print(f"Error: Data file '{args.data_file}' not found")
                sys.exit(1)

            try:
                with open(data_path, "r", encoding="utf-8") as f:
                    test_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in '{args.data_file}': {e}")
                sys.exit(1)

            # Test against baseline
            create_if_missing = not args.no_create
            generator.test_against_baseline(
                args.baseline_name, test_data, create_if_missing
            )
            print(f"✓ Test data matches baseline '{args.baseline_name}'")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except FileExistsError as e:
        print(f"Error: {e}")
        print("Use --overwrite to replace existing baseline")
        sys.exit(1)
    except BaselineNotFoundError as e:
        print(f"Warning: {e.message}")
        print("Review the generated baseline and re-run the test.")
        sys.exit(1)
    except BaselineComparisonError as e:
        print(f"❌ {e.message}")
        print("\nDifferences found:")
        for i, diff in enumerate(e.differences, 1):
            print(f"  {i}. {diff}")
        print(f"\nTotal differences: {len(e.differences)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
