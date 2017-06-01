"""Test the Optimize spell"""
import tempfile
import os
import shutil
import unittest

from os.path import dirname

from pyffi.formats.nif import NifFormat

dir_path = __file__
for i in range(4):  # recurse up to root repo dir
    dir_path = dirname(dir_path)
test_root = dir_path


class BaseFileTestCase(unittest.TestCase):
    def setUp(self):
        super(BaseFileTestCase, self).setUp()
        #.. set up that everyone needs ..
        self.input_files = os.path.join(test_root, 'spells', 'nif', 'files').replace("\\", "/")
        self.out = tempfile.mkdtemp()

    def readFile(self):
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
        #.. tear down that everyone needs ..
        super(BaseFileTestCase, self).tearDown()




