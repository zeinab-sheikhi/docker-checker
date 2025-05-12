# docker_scanner/logger.py
import logging
import sys

# ANSI color codes
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter that outputs logs in a multi-line colored format"""

    COLORS = {"DEBUG": BLUE, "INFO": GREEN, "WARNING": YELLOW, "ERROR": RED, "CRITICAL": RED}

    def format(self, record):
        # Save original levelname
        original_levelname = record.levelname

        # Colorize the level name
        color = self.COLORS.get(original_levelname, "")
        level_str = f"{color}{original_levelname}{RESET}"

        # Build formatted output
        message = record.getMessage()
        location = f"{record.pathname}:{record.lineno}"

        # Multi-line format:
        # LEVEL
        #     message
        #     path:line
        formatted = f"{level_str}:\n\t{message}\n\t{location}\n"

        return formatted


def setup_logger(name: str = "docker_scanner", level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure a logger with custom formatting.

    Args:
        name: The name for the logger
        level: The logging level (default: INFO)

    Returns:
        A configured Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Apply custom colored multi-line formatter
    colored_formatter = ColoredFormatter()
    console_handler.setFormatter(colored_formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)

    return logger


# Create a default application logger
app_logger = setup_logger("docker_scanner")


# Convenience function for importing
def get_logger(name: str | None = None) -> logging.Logger:
    """Get a logger with the given name or return the default app logger"""
    if name:
        return setup_logger(name)
    return app_logger
