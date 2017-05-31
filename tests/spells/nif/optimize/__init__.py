"""Test the Optimize spell"""
import tempfile
import os
import shutil
import unittest

from os.path import dirname
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

    def tearDown(self):
        shutil.rmtree(self.out)
        #.. tear down that everyone needs ..
        super(BaseFileTestCase, self).tearDown()




