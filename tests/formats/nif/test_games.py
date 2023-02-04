import pytest
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

    # 0: BSFadeNode
    block = data.blocks[0]
    assert isinstance(block, NifFormat.BSFadeNode)
    assert block.name == b"GenElecSwitch01"
    assert block.num_extra_data_list == 2
    assert int(block.flags) == 0x0008000e
    assert block.translation == NifFormat.Vector3.zero()
    assert block.rotation == NifFormat.Matrix33.identity()
    assert block.scale == 1.0
    assert block.num_properties == 0
    assert block.num_children == 1
    assert block.num_effects == 0

    # 1: BSXFlags
    block = data.blocks[1]
    assert isinstance(block, NifFormat.BSXFlags)
    assert block.name == b"BSX"
    assert block.integer_data == 11

    # 2: NiStringExtraData
    block = data.blocks[2]
    assert isinstance(block, NifFormat.NiStringExtraData)
    assert block.name == b"UPB"
    assert block.string_data == b"KFAccumRoot = \r\nUnyielding = 0\r\n"

    # 18: NiNode
    block = data.blocks[18]
    assert isinstance(block, NifFormat.NiNode)

    # 25: NiTriStrips
    block = data.blocks[25]
    assert isinstance(block, NifFormat.NiTriStrips)
    assert block.name == b"GenElecSwitch01:0"
    assert block.num_properties == 2

    # 29: NiTriStripsData
    block = data.blocks[29]
    assert isinstance(block, NifFormat.NiTriStripsData)
    assert block.num_vertices == 480
    assert block.num_triangles == 288
    assert block.num_strips == 122

    # 30: NiTriStrips
    block = data.blocks[30]
    assert isinstance(block, NifFormat.NiTriStrips)
    assert block.name == b"GenElecSwitch01:3"
    assert block.num_properties == 3

    # 34: NiTriStripsData
    block = data.blocks[34]
    assert isinstance(block, NifFormat.NiTriStripsData)
    assert block.num_vertices == 12
    assert block.num_triangles == 12
    assert block.num_strips == 2


def test_import_fallout4():
    data = read_file("fallout4_refrigerator.nif")
    assert data.version == NifFormat.version_number("20.2.0.7")
    assert data.user_version == 12
    assert data.bs_version == 130
    assert data.header.num_blocks == 37
    assert data.header.num_block_types == 18
    assert data.header.num_strings == 19

    # 0: NiNode
    block = data.blocks[0]
    assert isinstance(block, NifFormat.NiNode)
    assert block.name == b"PlayerHouse_KitchenRefrigerator01"
    assert block.num_extra_data_list == 1
    assert block.flags == 14
    assert block.translation == NifFormat.Vector3.zero()
    assert block.rotation == NifFormat.Matrix33.identity()
    assert block.scale == 1.0
    assert block.num_children == 2

    # 1: BSXFlags
    block = data.blocks[1]
    assert isinstance(block, NifFormat.BSXFlags)
    assert block.name == b"BSX"

    # 19: NiNode
    block = data.blocks[19]
    assert isinstance(block, NifFormat.NiNode)
    assert block.name == b"PlayerHouse_KitchenRefrigerator01_Mesh"
    assert block.num_extra_data_list == 0
    assert block.flags == 14
    assert block.translation == NifFormat.Vector3.zero()
    assert block.rotation == NifFormat.Matrix33.identity()
    assert block.scale == 1.0
    assert block.num_children == 3

    # 22: BSTriShape
    block = data.blocks[22]
    assert isinstance(block, NifFormat.BSTriShape)
    assert block.name == b"PlayerHouse_KitchenRefrigerator01_Mesh:31"
    assert block.num_extra_data_list == 0
    assert block.flags == 14
    assert block.translation == NifFormat.Vector3.zero()
    assert block.rotation == NifFormat.Matrix33.identity()
    assert block.scale == 1.0
    assert block.num_triangles == 146
    assert block.num_vertices == 202
    assert block.data_size == 7340

    # 27: BSTriShape
    block = data.blocks[27]
    assert isinstance(block, NifFormat.BSTriShape)
    assert block.name == b"PlayerHouse_KitchenRefrigerator01_Mesh:34"
    assert block.num_extra_data_list == 0
    assert block.flags == 14
    assert block.translation == NifFormat.Vector3.zero()
    assert block.rotation == NifFormat.Matrix33.identity()
    assert block.scale == 1.0
    assert block.num_triangles == 1771
    assert block.num_vertices == 1434
    assert block.data_size == 56514

    # 32: BSTriShape
    block = data.blocks[32]
    assert isinstance(block, NifFormat.BSTriShape)
    assert block.name == b"PlayerHouse_KitchenRefrigerator01_Mesh:113"
    assert block.num_extra_data_list == 0
    assert block.flags == 14
    assert block.translation == NifFormat.Vector3.zero()
    assert block.rotation == NifFormat.Matrix33.identity()
    assert block.scale == 1.0
    assert block.num_triangles == 2
    assert block.num_vertices == 4
    assert block.data_size == 156


def test_import_falloutnv():
    data = read_file("falloutnv_goldbar.nif")
    assert data.version == NifFormat.version_number("20.2.0.7")
    assert data.user_version == 11
    assert data.bs_version == 34
    assert data.header.num_blocks == 13
    assert data.header.num_block_types == 13
    assert data.header.num_strings == 4

    # 0: BSFadeNode
    block = data.blocks[0]
    assert isinstance(block, NifFormat.BSFadeNode)
    assert block.name == b"Scene Root"
    assert block.num_extra_data_list == 1
    assert int(block.flags) == 524302
    assert block.translation == NifFormat.Vector3.zero()
    assert block.rotation == NifFormat.Matrix33.identity()
    assert block.scale == 1.0
    assert block.num_properties == 0
    assert block.num_children == 1
    assert block.num_effects == 0

    # 1: BSXFlags
    block = data.blocks[1]
    assert isinstance(block, NifFormat.BSXFlags)
    assert block.name == b"BSX"
    assert block.integer_data == 3

    # 6: NiTriStrips
    block = data.blocks[6]
    assert isinstance(block, NifFormat.NiTriStrips)
    assert block.name == b"GoldBarGD"
    assert block.num_extra_data_list == 0
    assert block.flags == 524302
    assert block.translation == NifFormat.Vector3.zero()
    # assert block.rotation == 0 to bothered to actually
    assert block.num_properties == 4

    # 12: NiTriStripsData
    block = data.blocks[12]
    assert isinstance(block, NifFormat.NiTriStripsData)
    assert block.group_id == 0
    assert block.num_vertices == 120
    assert block.keep_flags == 0
    assert block.compress_flags == 0
    assert block.has_vertices
    assert block.has_normals
    assert block.bounding_sphere.center == NifFormat.Vector3.create(0, 0, 1.279867)
    assert block.bounding_sphere.radius == pytest.approx(9.251637)
    assert not block.has_vertex_colors
    assert block.num_triangles == 249
    assert block.num_strips == 1
    assert block.has_points


def test_import_morrowind():
    data = read_file("morrowind_mossyrock.nif")
    assert data.version == NifFormat.version_number("4.0.0.2")
    assert data.header.num_blocks == 11
    # TODO: All/some blocks


def test_import_oblivion():
    data = read_file("oblivion_chair.nif")
    assert data.version == NifFormat.version_number("20.0.0.5")
    assert data.user_version == 11
    assert data.bs_version == 11
    assert data.header.num_blocks == 39
    assert data.header.num_block_types == 14
    # TODO: All/some blocks


def test_import_skyrim():
    data = read_file("skyrim_cookiechip.nif")
    assert data.version == NifFormat.version_number("20.2.0.7")
    assert data.user_version == 12
    assert data.bs_version == 83
    assert data.header.num_blocks == 12
    assert data.header.num_block_types == 12
    assert data.header.num_strings == 4
    # TODO: All/some blocks


def test_import_skyrimse():
    data = read_file("skyrimse_cookiechip.nif")
    assert data.version == NifFormat.version_number("20.2.0.7")
    assert data.user_version == 12
    assert data.bs_version == 100
    assert data.header.num_blocks == 11
    assert data.header.num_block_types == 11
    assert data.header.num_strings == 4
    # TODO: All/some blocks
