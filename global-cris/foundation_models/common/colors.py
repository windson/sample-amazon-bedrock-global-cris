"""
ANSI color utilities for console output in advanced examples.
"""

# ANSI escape codes
GREEN = "\033[32m"
ORANGE = "\033[38;5;208m"
MAGENTA = "\033[35m"
DIM = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"


def status_color(value: bool) -> str:
    """Return green text for True, orange text for False."""
    color = GREEN if value else ORANGE
    return f"{color}{value}{RESET}"


def turn_header(turn_num: int, description: str) -> str:
    """Return a magenta-colored turn header."""
    return f"{MAGENTA}{BOLD}📝 Turn {turn_num}: {description}{RESET}"
