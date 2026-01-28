"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Optional


def setup_logging ():
    """Setup application logging configuration."""
   
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

# Create a global logger instance for the app
logger = logging.getLogger("er_app")
