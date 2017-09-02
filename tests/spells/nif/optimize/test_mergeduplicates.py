from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase

import pyffi
from pyffi.spells import Toaster

from nose.tools import assert_true, assert_false


class TestMergeDuplicatesOptimisationNif(BaseNifFileTestCase):
    # I didn't need setUp and tearDown here..

    def setUp(self):
        super(TestMergeDuplicatesOptimisationNif, self).setUp()
        self.src_name = "test_opt_mergeduplicates.nif"
        super(TestMergeDuplicatesOptimisationNif, self).copyFile()

    def test_non_interactive_opt_merge_duplicates(self):
        call_niftoaster("--raise", "opt_mergeduplicates", "--dry-run", "--noninteractive", "--verbose=1", self.dest_file)
    

class TestMergeDuplicatesGeomOptimisationNif(BaseNifFileTestCase):
    # I didn't need setUp and tearDown here..

    def setUp(self):
        super(TestMergeDuplicatesGeomOptimisationNif, self).setUp()
        self.src_name = "test_opt_dupgeomdata.nif"
        super(TestMergeDuplicatesGeomOptimisationNif, self).copyFile()

    def test_non_interactive_opt_merge_duplicates(self):
        pass
        # call_niftoaster("--raise", "opt_mergeduplicates", "--dry-run",  "--noninteractive", "--verbose=1", self.dest_file)

        """
            pyffi.toaster:INFO:=== tests/spells/nif/files/test_opt_dupgeomdata.nif ===
            pyffi.toaster:INFO:  --- opt_mergeduplicates ---
            pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
            pyffi.toaster:INFO:      ~~~ NiNode [Cube1] ~~~
            pyffi.toaster:INFO:        ~~~ NiTriShape [Tri Cube1] ~~~
            pyffi.toaster:INFO:          ~~~ NiTriShapeData [] ~~~
            pyffi.toaster:INFO:        ~~~ NiNode [Cube2] ~~~
            pyffi.toaster:INFO:          ~~~ NiTriShape [Tri Cube2] ~~~
            pyffi.toaster:INFO:            ~~~ NiTriShapeData [] ~~~
            pyffi.toaster:INFO:              removing duplicate branch
            pyffi.toaster:INFO:          ~~~ NiNode [Cube3] ~~~
            pyffi.toaster:INFO:            ~~~ NiTriShape [Tri Cube3] ~~~
            pyffi.toaster:INFO:              ~~~ NiTriShapeData [] ~~~
            pyffi.toaster:INFO:                removing duplicate branch
            pyffi.toaster:INFO:            ~~~ NiTriShape [Cube4] ~~~
            pyffi.toaster:INFO:              ~~~ NiTriShapeData [] ~~~
            pyffi.toaster:INFO:                removing duplicate branch
            pyffi.toaster:INFO:  writing to temporary file
            pyffi.toaster:INFO:Finished.
        """


def has_duplicates(root):
    """Method to verify if tree has duplicate branches"""
    for branch in root.tree():
        for other_branch in root.tree():
            if branch is not other_branch and branch.is_interchangeable(other_branch):
                return True
    return False


class TestExplicitMergeDuplicatesGeomOptimisationNif(BaseNifFileTestCase):
    # I didn't need setUp and tearDown here..

    def setUp(self):
        super(TestExplicitMergeDuplicatesGeomOptimisationNif, self).setUp()
        self.src_name = "test_opt_mergeduplicates.nif"
        super(TestExplicitMergeDuplicatesGeomOptimisationNif, self).copyFile()
        super(TestExplicitMergeDuplicatesGeomOptimisationNif, self).readNifData()

    def test_non_interactive_opt_merge_duplicates(self):
        # check that there are duplicates
        assert_true(has_duplicates(self.data.roots[0]))

        # run the spell that fixes this
        spell = pyffi.spells.nif.optimize.SpellMergeDuplicates(data=self.data)
        spell.recurse()

        assert_false(has_duplicates(self.data.roots[0]))