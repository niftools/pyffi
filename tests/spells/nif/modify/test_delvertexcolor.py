"""Tests for the modify_delvertexcolor spell"""
from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase

from nose.tools import assert_equals, assert_false, assert_true


class TestModifyDelBranchesNif(BaseNifFileTestCase):
    """Invoke the modify_delvertexcolor spell check through nif toaster"""

    def setUp(self):
        super(TestModifyDelBranchesNif, self).setUp()
        self.src_name = "test_vertexcolor.nif"
        super(TestModifyDelBranchesNif, self).copyFile()
        super(TestModifyDelBranchesNif, self).readNifData()

    def test_non_interactive_modify_delbranches(self):
        """Test that we can delete vertex colors"""
        blocks = [block.__class__.__name__ for block in self.data.blocks]
        expected = ['NiNode', 'NiTriStrips', 'NiStencilProperty', 'NiSpecularProperty', 'NiMaterialProperty',
                    'NiVertexColorProperty', 'NiTriStripsData']
        assert_equals(blocks, expected)
        assert_true(self.data.roots[0].children[0].data.has_vertex_colors)


        # delete vertex color
        call_niftoaster("--raise", "modify_delvertexcolor", "--noninteractive", "--verbose=1", self.dest_file)
        """
        pyffi.toaster:INFO:=== ...test_vertexcolor.nif ===
        pyffi.toaster:INFO:  --- modify_delvertexcolor ---
        pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
        pyffi.toaster:INFO:      ~~~ NiTriStrips [Cube] ~~~
        pyffi.toaster:INFO:        ~~~ NiVertexColorProperty [] ~~~
        pyffi.toaster:INFO:          stripping this branch
        pyffi.toaster:INFO:        ~~~ NiTriStripsData [] ~~~
        pyffi.toaster:INFO:          removing vertex colors
        pyffi.toaster:INFO:  writing ..._test_vertexcolor.nif
        pyffi.toaster:INFO:Finished.
        """

        super(TestModifyDelBranchesNif, self).readNifData()

        # check that file has no vertex color
        blocks = [block.__class__.__name__ for block in self.data.blocks]
        expected = ['NiNode', 'NiTriStrips', 'NiStencilProperty', 'NiSpecularProperty', 'NiMaterialProperty', 'NiTriStripsData']
        assert_equals(blocks, expected)
        assert_false(self.data.roots[0].children[0].data.has_vertex_colors)
