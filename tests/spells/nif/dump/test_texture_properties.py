"""Tests for the dump_tex spell"""
from tests.scripts.nif import call_niftoaster
from tests.utils import BaseNifFileTestCase


class TestDumpTextureDataNif(BaseNifFileTestCase):
    """Invoke the dump_tex spell check through nif toaster"""

    def setUp(self):
        super(TestDumpTextureDataNif, self).setUp()
        self.src_name = "test_dump_tex.nif"
        super(TestDumpTextureDataNif, self).copyFile()
        super(TestDumpTextureDataNif, self).readNifData()

    def test_non_interactive_dump_texture_properties(self):
        """Test that we extract texture and material information"""

        call_niftoaster("--raise", "dump_tex", "--noninteractive", "--verbose=1", self.dest_file)

        """
        pyffi.toaster:INFO:=== tests/spells/nif/files/test_dump_tex.nif ===
        pyffi.toaster:INFO:  --- dump_tex ---
        pyffi.toaster:INFO:    ~~~ NiNode [test] ~~~
        pyffi.toaster:INFO:      ~~~ NiTriShape [Cube] ~~~
        pyffi.toaster:INFO:        ~~~ NiMaterialProperty [CubeMaterial] ~~~
        pyffi.toaster:INFO:          ambient    0.76 0.43 0.43
        pyffi.toaster:INFO:          diffuse    0.92 0.77 0.09
        pyffi.toaster:INFO:          specular   0.45 0.19 0.77
        pyffi.toaster:INFO:          emissive   0.00 0.00 0.00
        pyffi.toaster:INFO:          glossiness 123.000000
        pyffi.toaster:INFO:          alpha      0.560000
        pyffi.toaster:INFO:        ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:          [base] bitmap2.dds
        pyffi.toaster:INFO:          [detail] bitmap1.dds
        pyffi.toaster:INFO:          apply mode 2
        pyffi.toaster:INFO:Finished.
        """

class TestDumpTextureDataNif(BaseNifFileTestCase):
    """Invoke the dump_tex spell check through nif toaster"""

    def setUp(self):
        super(TestDumpTextureDataNif, self).setUp()
        self.src_name = "test_fix_ffvt3rskinpartition.nif"
        super(TestDumpTextureDataNif, self).copyFile()
        super(TestDumpTextureDataNif, self).readNifData()

    def test_non_interactive_dump_texture_properties(self):
        """Test that we extract texture and material information"""

        call_niftoaster("--raise", "dump_tex", "--noninteractive", "--verbose=1", self.dest_file)

        """
        pyffi.toaster:INFO:=== tests/spells/nif/files/test_fix_ffvt3rskinpartition.nif ===
        pyffi.toaster:INFO:  --- dump_tex ---
        pyffi.toaster:INFO:    ~~~ NiNode [Bip01] ~~~
        pyffi.toaster:INFO:      ~~~ NiNode [Bip01 Pelvis] ~~~
        pyffi.toaster:INFO:        ~~~ NiNode [Bip01 Spine] ~~~
        pyffi.toaster:INFO:          ~~~ NiNode [Bip01 Spine1] ~~~
        pyffi.toaster:INFO:            ~~~ NiNode [Bip01 Spine2] ~~~
        pyffi.toaster:INFO:              ~~~ NiNode [Bip01 Neck] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 Head] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 L Clavicle] ~~~
        pyffi.toaster:INFO:                  ~~~ NiNode [Bip01 L UpperArm] ~~~
        pyffi.toaster:INFO:                    ~~~ NiNode [Bip01 L Forearm] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 R Clavicle] ~~~
        pyffi.toaster:INFO:                  ~~~ NiNode [Bip01 R UpperArm] ~~~
        pyffi.toaster:INFO:                    ~~~ NiNode [Bip01 R Forearm] ~~~
        pyffi.toaster:INFO:          ~~~ NiNode [Bip01 L Thigh] ~~~
        pyffi.toaster:INFO:            ~~~ NiNode [Bip01 L Calf] ~~~
        pyffi.toaster:INFO:              ~~~ NiNode [Bip01 L Foot] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 L Toe0] ~~~
        pyffi.toaster:INFO:          ~~~ NiNode [Bip01 R Thigh] ~~~
        pyffi.toaster:INFO:            ~~~ NiNode [Bip01 R Calf] ~~~
        pyffi.toaster:INFO:              ~~~ NiNode [Bip01 R Foot] ~~~
        pyffi.toaster:INFO:                ~~~ NiNode [Bip01 R Toe0] ~~~
        pyffi.toaster:INFO:      ~~~ NiTriShape [Body] ~~~
        pyffi.toaster:INFO:        ~~~ NiTexturingProperty [] ~~~
        pyffi.toaster:INFO:          [base] body.dds
        pyffi.toaster:INFO:          apply mode 2
        pyffi.toaster:INFO:        ~~~ NiMaterialProperty [Material] ~~~
        pyffi.toaster:INFO:          ambient    0.50 0.50 0.50
        pyffi.toaster:INFO:          diffuse    1.00 1.00 1.00
        pyffi.toaster:INFO:          specular   0.50 0.50 0.50
        pyffi.toaster:INFO:          emissive   0.00 0.00 0.00
        pyffi.toaster:INFO:          glossiness 12.500000
        pyffi.toaster:INFO:          alpha      1.000000
        pyffi.toaster:INFO:Finished.
        """
