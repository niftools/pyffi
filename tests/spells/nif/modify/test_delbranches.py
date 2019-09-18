"""Tests for the modify_delbranches spell and its friends"""
from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase

from nose.tools import assert_equals


class TestModifyDelBranchesNif(BaseNifFileTestCase):
    """Invoke the modify_delbranches spell check through nif toaster"""

    def setUp(self):
        super(TestModifyDelBranchesNif, self).setUp()
        self.src_name = "test_opt_mergeduplicates.nif"
        super(TestModifyDelBranchesNif, self).copyFile()
        super(TestModifyDelBranchesNif, self).readNifData()

    def test_non_interactive_modify_delbranches(self):
        props = ['NiNode', 'NiVertexColorProperty', 'NiZBufferProperty', 'NiStencilProperty', 'NiDitherProperty',
                 'NiNode', 'NiZBufferProperty', 'NiVertexColorProperty', 'NiStencilProperty', 'NiDitherProperty',
                 'NiTriStrips', 'NiTexturingProperty', 'NiSourceTexture', 'NiMaterialProperty', 'NiSpecularProperty',
                 'NiTriStripsData', 'NiTriStrips', 'NiTexturingProperty', 'NiSourceTexture', 'NiMaterialProperty',
                 'NiSpecularProperty', 'NiAlphaProperty', 'NiTriStripsData', 'NiTriStrips', 'NiTexturingProperty',
                 'NiSourceTexture', 'NiMaterialProperty', 'NiWireframeProperty', 'NiAlphaProperty', 'NiTriStripsData',
                 'NiTriStrips', 'NiTexturingProperty', 'NiSourceTexture', 'NiMaterialProperty', 'NiWireframeProperty',
                 'NiDitherProperty', 'NiTriStripsData']

        blocks = [block.__class__.__name__ for block in self.data.blocks]
        assert_equals(props, blocks)

        # strip properties
        call_niftoaster("--raise", "modify_delbranches", "-x", "NiProperty", "--noninteractive", "--verbose=1",
                        self.dest_file)

        """
        pyffi.toaster:INFO:=== tests/spells/nif/files/test_opt_mergeduplicates.nif ===
        pyffi.toaster:INFO:  --- modify_delbranches ---
        pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
        pyffi.toaster:INFO:      ~~~ NiVertexColorProperty [] ~~~
        pyffi.toaster:INFO:        stripping this branch
        pyffi.toaster:INFO:      ~~~ NiZBufferProperty [] ~~~
        pyffi.toaster:INFO:        stripping this branch
        pyffi.toaster:INFO:      ~~~ NiStencilProperty [] ~~~
        pyffi.toaster:INFO:        stripping this branch
        pyffi.toaster:INFO:      ~~~ NiDitherProperty [] ~~~
        pyffi.toaster:INFO:        stripping this branch
        pyffi.toaster:INFO:      ~~~ NiNode [Cone] ~~~
        pyffi.toaster:INFO:        ~~~ NiZBufferProperty [] ~~~
        pyffi.toaster:INFO:          stripping this branch
        pyffi.toaster:INFO:        ~~~ NiVertexColorProperty [] ~~~
        pyffi.toaster:INFO:          stripping this branch
        pyffi.toaster:INFO:        ~~~ NiStencilProperty [] ~~~
        pyffi.toaster:INFO:          stripping this branch
        pyffi.toaster:INFO:        ~~~ NiDitherProperty [] ~~~
        pyffi.toaster:INFO:          stripping this branch
        pyffi.toaster:INFO:        ~~~ NiTriStrips [Tri Cone 0] ~~~
        pyffi.toaster:INFO:          ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Red] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiSpecularProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiTriStripsData [] ~~~
        pyffi.toaster:INFO:        ~~~ NiTriStrips [Tri Cone 1] ~~~
        pyffi.toaster:INFO:          ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [AlsoRed] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiSpecularProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiAlphaProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiTriStripsData [] ~~~
        pyffi.toaster:INFO:        ~~~ NiTriStrips [Tri Cone 2] ~~~
        pyffi.toaster:INFO:          ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Skin] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiWireframeProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiAlphaProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiTriStripsData [] ~~~
        pyffi.toaster:INFO:        ~~~ NiTriStrips [Tri Cone 3] ~~~
        pyffi.toaster:INFO:          ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Red] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiWireframeProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiDitherProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiTriStripsData [] ~~~
        pyffi.toaster:INFO:  writing tests/spells/nif/files..._test_opt_mergeduplicates.nif
        pyffi.toaster:INFO:Finished.
        """
        # check that file no longer has properties
        super(TestModifyDelBranchesNif, self).readNifData()
        blocks = [block.__class__.__name__ for block in self.data.blocks]

        branches = ['NiNode', 'NiNode', 'NiTriStrips', 'NiTriStripsData', 'NiTriStrips',
                    'NiTriStripsData', 'NiTriStrips', 'NiTriStripsData', 'NiTriStrips', 'NiTriStripsData']
        assert_equals(blocks, branches)

    def test_non_interactive_modify_delalphaprop(self):
        """NifToaster modify_delalphaprop check"""

        blocks = [block.__class__.__name__ for block in self.data.blocks]
        # check that file has alpha properties

        branches = ['NiNode', 'NiVertexColorProperty', 'NiZBufferProperty', 'NiStencilProperty', 'NiDitherProperty',
                    'NiNode', 'NiZBufferProperty', 'NiVertexColorProperty', 'NiStencilProperty', 'NiDitherProperty',
                    'NiTriStrips', 'NiTexturingProperty', 'NiSourceTexture', 'NiMaterialProperty', 'NiSpecularProperty',
                    'NiTriStripsData', 'NiTriStrips', 'NiTexturingProperty', 'NiSourceTexture', 'NiMaterialProperty',
                    'NiSpecularProperty', 'NiAlphaProperty', 'NiTriStripsData', 'NiTriStrips', 'NiTexturingProperty',
                    'NiSourceTexture', 'NiMaterialProperty', 'NiWireframeProperty', 'NiAlphaProperty',
                    'NiTriStripsData', 'NiTriStrips', 'NiTexturingProperty', 'NiSourceTexture',
                    'NiMaterialProperty', 'NiWireframeProperty', 'NiDitherProperty', 'NiTriStripsData']

        assert_equals(blocks, branches)

        # strip properties
        call_niftoaster("--raise", "modify_delalphaprop", "--noninteractive", "--verbose=1", self.dest_file)
        """
        pyffi.toaster:INFO:=== tests/spells/nif/files/test_opt_mergeduplicates.nif ===
        pyffi.toaster:INFO:  --- modify_delalphaprop ---
        pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
        pyffi.toaster:INFO:      ~~~ NiVertexColorProperty [] ~~~
        pyffi.toaster:INFO:      ~~~ NiZBufferProperty [] ~~~
        pyffi.toaster:INFO:      ~~~ NiStencilProperty [] ~~~
        pyffi.toaster:INFO:      ~~~ NiDitherProperty [] ~~~
        pyffi.toaster:INFO:      ~~~ NiNode [Cone] ~~~
        pyffi.toaster:INFO:        ~~~ NiZBufferProperty [] ~~~
        pyffi.toaster:INFO:        ~~~ NiVertexColorProperty [] ~~~
        pyffi.toaster:INFO:        ~~~ NiStencilProperty [] ~~~
        pyffi.toaster:INFO:        ~~~ NiDitherProperty [] ~~~
        pyffi.toaster:INFO:        ~~~ NiTriStrips [Tri Cone 0] ~~~
        pyffi.toaster:INFO:          ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:            ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Red] ~~~
        pyffi.toaster:INFO:          ~~~ NiSpecularProperty [] ~~~
        pyffi.toaster:INFO:          ~~~ NiTriStripsData [] ~~~
        pyffi.toaster:INFO:        ~~~ NiTriStrips [Tri Cone 1] ~~~
        pyffi.toaster:INFO:          ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:            ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [AlsoRed] ~~~
        pyffi.toaster:INFO:          ~~~ NiSpecularProperty [] ~~~
        pyffi.toaster:INFO:          ~~~ NiAlphaProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiTriStripsData [] ~~~
        pyffi.toaster:INFO:        ~~~ NiTriStrips [Tri Cone 2] ~~~
        pyffi.toaster:INFO:          ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:            ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Skin] ~~~
        pyffi.toaster:INFO:          ~~~ NiWireframeProperty [] ~~~
        pyffi.toaster:INFO:          ~~~ NiAlphaProperty [] ~~~
        pyffi.toaster:INFO:            stripping this branch
        pyffi.toaster:INFO:          ~~~ NiTriStripsData [] ~~~
        pyffi.toaster:INFO:        ~~~ NiTriStrips [Tri Cone 3] ~~~
        pyffi.toaster:INFO:          ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:            ~~~ NiSourceTexture [] ~~~
        pyffi.toaster:INFO:          ~~~ NiMaterialProperty [Red] ~~~
        pyffi.toaster:INFO:          ~~~ NiWireframeProperty [] ~~~
        pyffi.toaster:INFO:          ~~~ NiDitherProperty [] ~~~
        pyffi.toaster:INFO:          ~~~ NiTriStripsData [] ~~~
        pyffi.toaster:INFO:  writing ..._test_opt_mergeduplicates.nif
        pyffi.toaster:INFO:Finished.
        """

        super(TestModifyDelBranchesNif, self).readNifData()

        # check that file no longer has properties
        blocks = [block.__class__.__name__ for block in self.data.blocks]
        branches = ['NiNode', 'NiVertexColorProperty', 'NiZBufferProperty', 'NiStencilProperty', 'NiDitherProperty',
                    'NiNode', 'NiZBufferProperty', 'NiVertexColorProperty', 'NiStencilProperty', 'NiDitherProperty',
                    'NiTriStrips', 'NiTexturingProperty', 'NiSourceTexture', 'NiMaterialProperty', 'NiSpecularProperty',
                    'NiTriStripsData', 'NiTriStrips', 'NiTexturingProperty', 'NiSourceTexture', 'NiMaterialProperty',
                    'NiSpecularProperty', 'NiTriStripsData', 'NiTriStrips', 'NiTexturingProperty', 'NiSourceTexture',
                    'NiMaterialProperty', 'NiWireframeProperty', 'NiTriStripsData', 'NiTriStrips',
                    'NiTexturingProperty', 'NiSourceTexture', 'NiMaterialProperty', 'NiWireframeProperty',
                    'NiDitherProperty', 'NiTriStripsData']

        assert_equals(blocks, branches)