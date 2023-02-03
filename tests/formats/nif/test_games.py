from os import path
from os.path import dirname

from pyffi.formats.nif import NifFormat

dir_path = __file__
for i in range(1):  # recurse up to root repo dir
    dir_path = dirname(dir_path)
test_root = dir_path


def read_file(name: str):
    data = NifFormat.Data()
    with open(path.join(test_root, "files", name), 'rb') as stream:
        data.read(stream)
    return data


def test_import_fallout3():
    data = read_file("fallout3_switch.nif")
    assert data.version == NifFormat.version_number("20.2.0.7")
    assert data.user_version == 11
    assert data.bs_version == 34
    assert data.header.num_blocks == 46
    assert data.header.num_block_types == 24
    assert data.header.num_strings == 18
    # TODO: All/some blocks


def test_import_fallout4():
    data = read_file("fallout4_refrigerator.nif")
    assert data.version == NifFormat.version_number("20.2.0.7")
    assert data.user_version == 12
    assert data.bs_version == 130
    assert data.header.num_blocks == 37
    assert data.header.num_block_types == 18
    assert data.header.num_strings == 19
    # TODO: All/some blocks


def test_import_falloutnv():  # TODO
    data = read_file("falloutnv_goldbar.nif")
    assert data.version == NifFormat.version_number("20.2.0.7")
    assert data.user_version == 11
    assert data.bs_version == 34
    assert data.header.num_blocks == 13
    assert data.header.num_block_types == 13
    assert data.header.num_strings == 4
    # TODO: All/some blocks


def test_import_morrowind():  # TODO
    data = read_file("morrowind_mossyrock.nif")
    assert data.version == NifFormat.version_number("4.0.0.2")
    assert data.header.num_blocks == 11
    # TODO: All/some blocks


def test_import_oblivion():  # TODO
    data = read_file("oblivion_chair.nif")
    assert data.version == NifFormat.version_number("20.0.0.5")
    assert data.user_version == 11
    assert data.bs_version == 11
    assert data.header.num_blocks == 39
    assert data.header.num_block_types == 14
    # TODO: All/some blocks


def test_import_skyrim():  # TODO
    data = read_file("skyrim_cookiechip.nif")
    assert data.version == NifFormat.version_number("20.2.0.7")
    assert data.user_version == 12
    assert data.bs_version == 83
    assert data.header.num_blocks == 12
    assert data.header.num_block_types == 12
    assert data.header.num_strings == 4
    # TODO: All/some blocks


def test_import_skyrimse():  # TODO
    data = read_file("skyrimse_cookiechip.nif")
    assert data.version == NifFormat.version_number("20.2.0.7")
    assert data.user_version == 12
    assert data.bs_version == 100
    assert data.header.num_blocks == 11
    assert data.header.num_block_types == 11
    assert data.header.num_strings == 4
    # TODO: All/some blocks
