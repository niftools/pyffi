"""Tests for pyffi."""

import logging
import sys

test_logger = logging.getLogger("pyffi:testlogger")
test_logger.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler(sys.stdout)
loghandler.setLevel(logging.DEBUG)
logformatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
loghandler.setFormatter(logformatter)
test_logger.addHandler(loghandler)
