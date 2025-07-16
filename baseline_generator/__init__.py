"""Baseline Generator - A Python package for generating and managing test baselines."""

__version__ = "0.1.0"
__author__ = "Alejandro"

from .cli import main as cli_main
from .generator import BaselineComparisonError, BaselineGenerator, BaselineNotFoundError

__all__ = [
    "BaselineGenerator",
    "BaselineComparisonError",
    "BaselineNotFoundError",
    "cli_main",
]
