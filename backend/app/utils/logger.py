"""Logging utility for consistent backend diagnostics."""

import logging
import sys


def configure_logging(debug: bool = False) -> logging.Logger:
    """Configure and return the root application logger."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    return logging.getLogger("skillgap_ai")
