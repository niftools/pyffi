"""Tests for utility classes"""

import nose
import nose.tools
import tempfile
import os
import shutil
import unittest
from os.path import dirname
from pyffi.formats.nif import NifFormat


def assert_tuple_values(a, b):
    """Wrapper func to cleanly assert tuple values"""
    for i, j in zip(a, b):
        nose.tools.assert_almost_equal(i, j)

dir_path = __file__
for i in range(2):  # recurse up to root repo dir
    dir_path = dirname(dir_path)
test_root = dir_path


class BaseFileTestCase(unittest.TestCase):

    def setUp(self):
        super(BaseFileTestCase, self).setUp()
        # set up that everyone needs ..
        self.input_files = os.path.join(test_root, 'spells', 'nif', 'files').replace("\\", "/")
        self.out = tempfile.mkdtemp()

    def copyFile(self):
        self.src_file = os.path.join(self.input_files, self.src_name)
        self.dest_file = os.path.join(self.out, self.src_name)
        shutil.copyfile(self.src_file, self.dest_file)
        assert os.path.exists(self.dest_file)

    def readNifData(self):
        self.data = NifFormat.Data()
        stream = open(self.src_file, "rb")
        self.data.read(stream)

    def tearDown(self):
        shutil.rmtree(self.out)
        # tear down that everyone needs ..
        super(BaseFileTestCase, self).tearDown()