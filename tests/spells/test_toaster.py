"""Tests for pyffi."""
import tempfile
import os
import shutil

from nose.tools import assert_true, assert_false

from pyffi.formats.nif import NifFormat
from pyffi.spells import Toaster


class MyToaster(Toaster):
    FILEFORMAT = NifFormat


class TestToaster:
    """Test class for spell base."""

    def test_toaster_default_admissible(self):
        """# no include or exclude: all admissible"""
        toaster = MyToaster()
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiProperty))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiNode))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiAVObject))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiLODNode))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiMaterialProperty))

    def test_toaster_exclude(self):
        """Test exclude NiProperty and NiNode inherited types"""
        toaster = MyToaster(options={"exclude": ["NiProperty", "NiNode"]})
        assert_false(toaster.is_admissible_branch_class(NifFormat.NiProperty))
        assert_false(toaster.is_admissible_branch_class(NifFormat.NiNode))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiAVObject))
        assert_false(toaster.is_admissible_branch_class(NifFormat.NiLODNode))
        assert_false(toaster.is_admissible_branch_class(NifFormat.NiMaterialProperty))


    def test_toaster_include(self):
        """Test include only NiProperty and NiNode inherited types"""
        toaster = MyToaster(options={"include": ["NiProperty", "NiNode"]})
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiProperty))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiNode))
        assert_false(toaster.is_admissible_branch_class(NifFormat.NiAVObject))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiLODNode))  # NiNode subclass!
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiMaterialProperty))  # NiProperties are!


    def test_toaster_include_and_exclude(self):
        """Test include NiProperty and NiNode, exclude NiMaterialProp and NiLODNode"""
        toaster = MyToaster(options={"include": ["NiProperty", "NiNode"],
                                     "exclude": ["NiMaterialProperty", "NiLODNode"]})
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiProperty))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiNode))
        assert_false(toaster.is_admissible_branch_class(NifFormat.NiAVObject))
        assert_false(toaster.is_admissible_branch_class(NifFormat.NiLODNode))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiSwitchNode))
        assert_false(toaster.is_admissible_branch_class(NifFormat.NiMaterialProperty))
        assert_true(toaster.is_admissible_branch_class(NifFormat.NiAlphaProperty))


class TestIniParser:
    """Test the Ini parser"""

    from os.path import dirname
    dir_path = __file__
    for i in range(2):  # recurse up to root repo dir
        dir_path = dirname(dir_path)
    test_root = dir_path
    input_files = os.path.join(test_root, 'spells', 'nif', 'files').replace("\\", "/")
    out = None

    def setup(self):
        self.out = tempfile.mkdtemp()

    def teardown(self):
        shutil.rmtree(self.out)

    def test_config_input(self):
        """Test config file input with delete branch spell"""
        src_file = os.path.join(self.input_files, 'test_vertexcolor.nif').replace("\\", "/")
        assert os.path.exists(src_file)

        import pyffi.spells.nif
        import pyffi.spells.nif.modify

        cfg = tempfile.NamedTemporaryFile(delete=False)
        cfg.write(b"[main]\n")
        cfg.write(b"spell = modify_delbranches\n")
        cfg.write("folder = {0}\n".format(src_file).encode())
        cfg.write(b"[options]\n")
        cfg.write("source-dir = {0}\n".format(self.test_root.replace("\\", "/")).encode())
        cfg.write("dest-dir = {0}\n".format(self.out.replace("\\", "/")).encode())
        cfg.write(b"exclude = NiVertexColorProperty NiStencilProperty\n")
        cfg.write(b"skip = 'testing quoted string'    normal_string\n")
        cfg.close()

        class TestDelToaster(pyffi.spells.nif.NifToaster):
            """Test Spell"""
            SPELLS = [pyffi.spells.nif.modify.SpellDelBranches]

        from pyffi.spells import fake_logger
        toaster = TestDelToaster(logger=fake_logger)
        import sys
        default_ini = os.path.join(self.test_root, "utilities", "toaster", "default.ini").replace("\\", "/")
        sys.argv = ["niftoaster.py", "--ini-file={0}".format(default_ini),
                    "--ini-file={0}".format(cfg.name), "--noninteractive", "--jobs=1"]
        toaster.cli()

        dest_file = os.path.join(self.out, 'spells', 'nif', 'files', 'test_vertexcolor.nif').replace("\\", "/")
        assert os.path.exists(dest_file.replace("\\", "/"))

        # TODO - Assert on file contents
        """
        pyffi.toaster: INFO: == = ...
        pyffi.toaster: INFO:  --- modify_delbranches - --
        pyffi.toaster: INFO:    ~~~ NiNode[Scene Root] ~~~
        pyffi.toaster: INFO:      ~~~ NiTriStrips[Cube] ~~~
        pyffi.toaster: INFO:        ~~~ NiStencilProperty[]~~~
        pyffi.toaster: INFO:          stripping this branch
        pyffi.toaster: INFO:        ~~~ NiSpecularProperty[] ~~~
        pyffi.toaster: INFO:        ~~~ NiMaterialProperty[Material] ~~~
        pyffi.toaster: INFO:        ~~~ NiVertexColorProperty[] ~~~
        pyffi.toaster: INFO:          stripping this branch
        pyffi.toaster: INFO:        ~~~ NiTriStripsData[] ~~~
        pyffi.toaster: INFO:creating destinationpath...
        pyffi.toaster: INFO:  writing...
        pyffi.toaster: INFO:Finished.

        applypatch: False
        archives: False
        arg:
        createpatch: False
        destdir: ...
        diffcmd:
        dryrun: False
        examples: False
        exclude: ['NiVertexColorProperty', 'NiStencilProperty']
        gccollect: False
        helpspell: False
        include: []
        inifile:
        interactive: False
        jobs: 1
        only: []
        patchcmd:
        pause: False
        prefix:
        raisetesterror: False
        refresh: 32
        resume: False
        series: False
        skip: ['testing quoted string', 'normal_string']
        sourcedir: ...
        spells: False
        suffix:
        verbose: 1
        """

        os.remove(dest_file)

        for name, value in sorted(toaster.options.items()):
            fake_logger.info("%s: %s" % (name, value))




