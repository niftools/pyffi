"""Tests for pyffi."""

import logging
import sys

logger = logging.getLogger("pyffi:testlogger")
logger.setLevel(logging.DEBUG)
loghandler = logging.StreamHandler(sys.stdout)
loghandler.setLevel(logging.DEBUG)
logformatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
loghandler.setFormatter(logformatter)
logger.addHandler(loghandler)
