"""Alpha calculation and formatting helpers."""

import decimal
from pathlib import Path

__all__ = ["AlphaFormatter", "calculate_alpha"]


class AlphaFormatter:
    def format_alpha(self, value):
        return f"alpha={value}"


def calculate_alpha(value):
    Path(".")
    return decimal.Decimal(value)
