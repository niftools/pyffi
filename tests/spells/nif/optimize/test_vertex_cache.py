from tests.utils import BaseNifFileTestCase
from nose.tools import assert_equals

import pyffi


class TestVertexCacheOptimisationNif(BaseNifFileTestCase):
    """Regression test for vertex cache algorithm"""

    def setUp(self):
        super(TestVertexCacheOptimisationNif, self).setUp()
        self.src_name = "test_opt_vertex_cache.nif"
        super(TestVertexCacheOptimisationNif, self).copyFile()
        super(TestVertexCacheOptimisationNif, self).readNifData()

        assert_equals(self.data.roots[0].children[0].data.num_vertices, 32)

    def test_non_interactive_opt_merge_duplicates(self):
        spell = pyffi.spells.nif.optimize.SpellOptimizeGeometry(data=self.data)
        spell.recurse()

        assert_equals(self.data.roots[0].children[0].data.num_vertices, 17)
        """
        pyffi.toaster:INFO:--- opt_geometry ---
        pyffi.toaster:INFO:  ~~~ NiNode [fan] ~~~
        pyffi.toaster:INFO:    ~~~ NiTriShape [fan01] ~~~
        pyffi.toaster:INFO:      removing duplicate vertices
        pyffi.toaster:INFO:      (num vertices was 32 and is now 32)
        pyffi.toaster:INFO:      optimizing triangle ordering
        pyffi.toaster:INFO:      (ATVR stable at 1.059)
        pyffi.toaster:INFO:      optimizing vertex ordering
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:WARNING:unused vertex
        pyffi.toaster:INFO:      recalculating tangent space """
