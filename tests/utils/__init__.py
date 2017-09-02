"""Tests for utility classes"""

import nose
import nose.tools
import tempfile
import os
import shutil
import unittest
from os.path import dirname

from pyffi.formats.cgf import CgfFormat
from pyffi.formats.nif import NifFormat


def assert_tuple_values(a, b):
    """Wrapper func to cleanly assert tuple values"""
    for elem, j in zip(a, b):
        nose.tools.assert_almost_equal(elem, j, places=3)

dir_path = __file__
for i in range(2):  # recurse up to root repo dir
    dir_path = dirname(dir_path)
test_root = dir_path


class BaseFileTestCase(unittest.TestCase):
    FORMAT = ""

    def setUp(self):
        super(BaseFileTestCase, self).setUp()
        # set up that everyone needs ..
        self.input_files = os.path.join(test_root, 'spells', self.FORMAT, 'files').replace("\\", "/")
        self.out = tempfile.mkdtemp()

    def copyFile(self):
        self.src_file = os.path.join(self.input_files, self.src_name)
        self.dest_file = os.path.join(self.out, self.src_name)
        shutil.copyfile(self.src_file, self.dest_file)
        assert os.path.exists(self.dest_file)

    def tearDown(self):
        shutil.rmtree(self.out)
        # tear down that everyone needs ..
        super(BaseFileTestCase, self).tearDown()


class BaseNifFileTestCase(BaseFileTestCase):
    FORMAT = 'nif'

    def readNifData(self):
        self.data = NifFormat.Data()
        stream = open(self.dest_file, "rb")
        self.data.read(stream)


class BaseCgfFileTestCase(BaseFileTestCase):
    FORMAT = 'cgf'

    def readCgfData(self):
        self.data = CgfFormat.Data()
        stream = open(self.dest_file, "rb")
        self.data.read(stream)
