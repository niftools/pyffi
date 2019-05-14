"""Tests for pyffi."""

import logging
import sys

from logging.handlers import RotatingFileHandler

# Get Logger
test_logger = logging.getLogger("pyffi:testlogger")
test_logger.setLevel(logging.DEBUG)

# Get Handlers
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setLevel(logging.DEBUG)
file_handler = RotatingFileHandler("tests\\test.log", mode='w', maxBytes=64000000, backupCount=3)

# Set Formatting
# Make this a better format with more information
log_formatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
log_handler.setFormatter(log_formatter)
file_handler.setFormatter(log_formatter)

# Add Handlers
test_logger.addHandler(log_handler)
test_logger.addHandler(file_handler)
