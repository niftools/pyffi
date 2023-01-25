"""Tests for the niftoaster script"""

import os
import os.path

from nose.tools import assert_equal, assert_almost_equal, raises

from tests.scripts.nif import call_niftoaster

nif_dir = "tests/spells/nif/files/"


@raises(SystemExit)  # --help uses sys.exit()
def test_help():
    """Tests spell help"""
    call_niftoaster("--raise", "--help")


def test_examples():
    """Tests example"""
    call_niftoaster("--raise", "--examples")


def test_spells():
    """Tests spells"""
    call_niftoaster("--raise", "--spells")


@raises(AttributeError)
def test_raise():
    """Test exception raised on invalid nif"""
    call_niftoaster("--raise", "check_readwrite", nif_dir + "invalid.nif")


def test_no_raise():
    """Test ignore exception raised on invalid nif"""
    toaster = call_niftoaster("check_readwrite", nif_dir + "invalid.nif")
    assert_equal(sorted(toaster.files_failed), [nif_dir + "invalid.nif"])


def test_check_readwrite():
    """Test basic read nif"""
    for filename in ["nds.nif", "neosteam.nif", "test.nif"]:
        file_path = nif_dir + "{0}".format(filename)
        toaster = call_niftoaster("--raise", "check_readwrite", file_path)
        assert_equal(sorted(toaster.files_done), [file_path])


def test_check_skip_only():
    """Test skip NIF files using filters and type"""
    toaster = call_niftoaster(
        *("--raise --skip texture --skip skin --only fix_t --only center check_nop {0}".format(nif_dir).split()))
    assert_equal(sorted(toaster.files_done), [
        nif_dir + 'test_centerradius.nif',
        nif_dir + 'test_fix_tangentspace.nif'])

    assert_equal(sorted(toaster.files_skipped), [
        nif_dir + 'invalid.nif',
        nif_dir + 'nds.nif',
        nif_dir + 'neosteam.nif',
        nif_dir + 'test.nif',
        nif_dir + 'test_check_tangentspace1.nif',
        nif_dir + 'test_check_tangentspace2.nif',
        nif_dir + 'test_check_tangentspace3.nif',
        nif_dir + 'test_check_tangentspace4.nif',
        nif_dir + 'test_convexverticesshape.nif',
        nif_dir + 'test_dump_tex.nif',
        nif_dir + 'test_fix_clampmaterialalpha.nif',
        nif_dir + 'test_fix_cleanstringpalette.nif',
        nif_dir + 'test_fix_detachhavoktristripsdata.nif',
        nif_dir + 'test_fix_disableparallax.nif',
        nif_dir + 'test_fix_ffvt3rskinpartition.nif',
        nif_dir + 'test_fix_mergeskeletonroots.nif',
        nif_dir + 'test_fix_texturepath.nif',
        nif_dir + 'test_grid_128x128.nif',
        nif_dir + 'test_grid_64x64.nif',
        nif_dir + 'test_mopp.nif',
        nif_dir + 'test_opt_collision_complex_mopp.nif',
        nif_dir + 'test_opt_collision_mopp.nif',
        nif_dir + 'test_opt_collision_packed.nif',
        nif_dir + 'test_opt_collision_to_boxshape.nif',
        nif_dir + 'test_opt_collision_to_boxshape_notabox.nif',
        nif_dir + 'test_opt_collision_unpacked.nif',
        nif_dir + 'test_opt_delunusedbones.nif',
        nif_dir + 'test_opt_dupgeomdata.nif',
        nif_dir + 'test_opt_dupverts.nif',
        nif_dir + 'test_opt_emptyproperties.nif',
        nif_dir + 'test_opt_grid_layout.nif',
        nif_dir + 'test_opt_mergeduplicates.nif',
        nif_dir + 'test_opt_vertex_cache.nif',
        nif_dir + 'test_opt_zeroscale.nif',
        nif_dir + 'test_skincenterradius.nif',
        nif_dir + 'test_vertexcolor.nif',
    ])
    assert_equal(toaster.files_failed, set([]))


def test_prefix_suffix():
    """Test add prefix and suffix to output"""
    call_niftoaster(
        *("--raise --prefix=pre_ --suffix=_suf --noninteractive optimize {0}test.nif".format(nif_dir).split()))
    assert_equal(os.path.exists(nif_dir + "pre_test_suf.nif"), True)
    os.remove(nif_dir + "pre_test_suf.nif")


# TODO Move to spell test
def test_check_bhkbodycenter():
    """Test body centre spell"""
    testfile = nif_dir + "test_fix_detachhavoktristripsdata.nif"
    toaster = call_niftoaster("--raise", "check_bhkbodycenter", testfile)
    orig = toaster.files_done[testfile][0]["center"]["orig"]
    calc = toaster.files_done[testfile][0]["center"]["calc"]
    assert_equal(orig, (0.0, 0.0, 0.0, 0.0))
    assert_almost_equal(calc[0], -1.08541444)
    assert_almost_equal(calc[1], 18.46527444)
    assert_almost_equal(calc[2], 6.88672184)
    assert_almost_equal(calc[3], 0.0)


def test_check_centerradius():
    """Test body centre spell"""
    testfile = nif_dir + "test_centerradius.nif"
    toaster = call_niftoaster("--raise", "check_centerradius", testfile)
    vertex_outside = toaster.files_done[testfile][0]["vertex_outside"]
    orig_center = toaster.files_done[testfile][0]["center"]["orig"]
    calc_center = toaster.files_done[testfile][0]["center"]["calc"]
    orig_radius = toaster.files_done[testfile][0]["radius"]["orig"]
    calc_radius = toaster.files_done[testfile][0]["radius"]["calc"]
    assert_equal(vertex_outside, (10.0, -10.0, -10.0))
    assert_equal(orig_center, (-1.0, 0.0, 0.0))
    assert_almost_equal(orig_radius, 10.0)
    assert_almost_equal(calc_radius, 17.32050890)


"""
The check_skincenterradius spell
--------------------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "check_skincenterradius", nif_dir + "test_skincenterradius.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_skincenterradius.nif ===
pyffi.toaster:INFO:  --- check_skincenterradius ---
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
pyffi.toaster:INFO:        getting skindata block bounding spheres
pyffi.toaster:INFO:        recalculating bounding spheres
pyffi.toaster:INFO:        comparing old and new spheres
pyffi.toaster:ERROR:Bip01 L Foot center does not match; original [  0.000  0.000  0.000 ], calculated [  3.109  2.224 -0.117 ]
pyffi.toaster:ERROR:Bip01 L Foot radius does not match; original 0.0, calculated 5.48116622473
pyffi.toaster:INFO:Finished.

The check_convexverticesshape spell
-----------------------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "check_convexverticesshape", nif_dir + "test_convexverticesshape.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_convexverticesshape.nif ===
pyffi.toaster:INFO:  --- check_convexverticesshape ---
pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
pyffi.toaster:INFO:      ~~~ bhkCollisionObject [] ~~~
pyffi.toaster:INFO:        ~~~ bhkRigidBody [] ~~~
pyffi.toaster:INFO:          ~~~ bhkConvexVerticesShape [] ~~~
pyffi.toaster:INFO:            checking vertices and planes
pyffi.toaster:ERROR:vertex [  0.000  0.000  1.500 ] does not intersect with any plane
pyffi.toaster:INFO:      ~~~ NiTriStrips [Sphere] ~~~
pyffi.toaster:INFO:Finished.

The check_mopp spell
--------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=2", "--raise", "check_mopp", nif_dir + "test_mopp.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_mopp.nif ===
pyffi.nif.data:DEBUG:Reading header at 0x00000000
pyffi.nif.data:DEBUG:Version 0x14000005
pyffi.nif.data:DEBUG:Reading NiNode block at 0x000000DC
pyffi.nif.data:DEBUG:Reading BSXFlags block at 0x0000013C
pyffi.nif.data:DEBUG:Reading hkPackedNiTriStripsData block at 0x00000147
pyffi.nif.data:DEBUG:Reading bhkPackedNiTriStripsShape block at 0x00000BC3
pyffi.nif.data:DEBUG:Reading bhkMoppBvTreeShape block at 0x00000C09
pyffi.nif.data:DEBUG:Reading bhkRigidBody block at 0x0000104D
pyffi.nif.data:DEBUG:Reading bhkCollisionObject block at 0x00001139
pyffi.toaster:INFO:  --- check_mopp ---
pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
pyffi.toaster:INFO:      ~~~ bhkCollisionObject [] ~~~
pyffi.toaster:INFO:        ~~~ bhkRigidBody [] ~~~
pyffi.toaster:INFO:          ~~~ bhkMoppBvTreeShape [] ~~~
pyffi.toaster:INFO:            recalculating mopp origin and scale
pyffi.toaster:WARNING:origin mismatch
pyffi.toaster:WARNING:(was [ -1.670 -1.532 -1.444 ] and is now [ -1.760 -1.622 -1.534 ])
pyffi.toaster:WARNING:scale mismatch
pyffi.toaster:WARNING:(was 5308158.0 and is now 5020014.51438)
pyffi.toaster:INFO:            parsing mopp
pyffi.mopp:DEBUG:   0:0x28  0 254 [ bound Z ] 
pyffi.mopp:DEBUG:   3:0x27  0 242 [ bound Y ] 
pyffi.mopp:DEBUG:   6:0x26  0 255 [ bound X ] 
pyffi.mopp:DEBUG:   9:0x12  148 102 [ branch Z -> 13: 27: ] 
pyffi.mopp:DEBUG:     if: 
pyffi.mopp:DEBUG:  13:  0x24  113 76 [ branch ? -> 48: 20: ] 
pyffi.mopp:DEBUG:       if: 
pyffi.mopp:DEBUG:  48:    0x28  8 148 [ bound Z ] 
pyffi.mopp:DEBUG:  51:    0x26  16 251 [ bound X ] 
pyffi.mopp:DEBUG:  54:    0x10  114 85 [ branch X -> 58: 120: ] 
pyffi.mopp:DEBUG:         if: 
pyffi.mopp:DEBUG:  58:      0x12  57 42 [ branch Z -> 62: 70: ] 
pyffi.mopp:DEBUG:           if: 
pyffi.mopp:DEBUG:  62:        0x27  43 82 [ bound Y ] 
pyffi.mopp:DEBUG:  65:        0x26  45 104 [ bound X ] 
pyffi.mopp:DEBUG:  68:        0x50  92 [ triangle 92 ] 
pyffi.mopp:DEBUG:           else: 
pyffi.mopp:DEBUG:  70:        0x12  105 83 [ branch Z -> 74: 94: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG:  74:          0x11  46 32 [ branch Y -> 78: 82: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG:  78:            0x26  62 114 [ bound X ] 
pyffi.mopp:DEBUG:  81:            0x44  [ triangle 20 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG:  82:            0x26  16 90 [ bound X ] 
pyffi.mopp:DEBUG:  85:            0x10  64 45 [ branch X -> 89: 90: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG:  89:              0x42  [ triangle 18 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG:  90:              0x27  32 79 [ bound Y ] 
pyffi.mopp:DEBUG:  93:              0x43  [ triangle 19 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG:  94:          0x10  88 62 [ branch X -> 98: 115: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG:  98:            0x14  99 91 [ branch ? -> 102: 107: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 102:              0x27  17 72 [ bound Y ] 
pyffi.mopp:DEBUG: 105:              0x50  65 [ triangle 65 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 107:              0x27  32 113 [ bound Y ] 
pyffi.mopp:DEBUG: 110:              0x26  16 64 [ bound X ] 
pyffi.mopp:DEBUG: 113:              0x50  66 [ triangle 66 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 115:            0x27  12 35 [ bound Y ] 
pyffi.mopp:DEBUG: 118:            0x50  64 [ triangle 64 ] 
pyffi.mopp:DEBUG:         else: 
pyffi.mopp:DEBUG: 120:      0x27  7 94 [ bound Y ] 
pyffi.mopp:DEBUG: 123:      0x12  62 42 [ branch Z -> 127: 147: ] 
pyffi.mopp:DEBUG:           if: 
pyffi.mopp:DEBUG: 127:        0x27  31 92 [ bound Y ] 
pyffi.mopp:DEBUG: 130:        0x26  87 235 [ bound X ] 
pyffi.mopp:DEBUG: 133:        0x10  183 167 [ branch X -> 137: 145: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 137:          0x17  101 91 [ branch ? -> 141: 143: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 141:            0x50  91 [ triangle 91 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 143:            0x50  90 [ triangle 90 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 145:          0x50  89 [ triangle 89 ] 
pyffi.mopp:DEBUG:           else: 
pyffi.mopp:DEBUG: 147:        0x10  169 155 [ branch X -> 151: 174: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 151:          0x27  7 46 [ bound Y ] 
pyffi.mopp:DEBUG: 154:          0x12  108 83 [ branch Z -> 158: 170: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 158:            0x1B  147 145 [ branch ? -> 162: 166: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 162:              0x28  42 86 [ bound Z ] 
pyffi.mopp:DEBUG: 165:              0x45  [ triangle 21 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 166:              0x26  111 169 [ bound X ] 
pyffi.mopp:DEBUG: 169:              0x46  [ triangle 22 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 170:            0x27  7 20 [ bound Y ] 
pyffi.mopp:DEBUG: 173:            0x30  [ triangle 0 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 174:          0x28  46 133 [ bound Z ] 
pyffi.mopp:DEBUG: 177:          0x11  34 31 [ branch Y -> 181: 188: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 181:            0x28  46 108 [ bound Z ] 
pyffi.mopp:DEBUG: 184:            0x26  155 211 [ bound X ] 
pyffi.mopp:DEBUG: 187:            0x47  [ triangle 23 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 188:            0x10  235 209 [ branch X -> 192: 197: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 192:              0x28  46 104 [ bound Z ] 
pyffi.mopp:DEBUG: 195:              0x50  88 [ triangle 88 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 197:              0x50  42 [ triangle 42 ] 
pyffi.mopp:DEBUG:       else: 
pyffi.mopp:DEBUG:  20:    0x23  135 100 [ branch ? -> 199: 330: ] 
pyffi.mopp:DEBUG:         if: 
pyffi.mopp:DEBUG: 199:      0x10  63 40 [ branch X -> 203: 247: ] 
pyffi.mopp:DEBUG:           if: 
pyffi.mopp:DEBUG: 203:        0x28  39 125 [ bound Z ] 
pyffi.mopp:DEBUG: 206:        0x12  105 87 [ branch Z -> 210: 222: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 210:          0x27  76 195 [ bound Y ] 
pyffi.mopp:DEBUG: 213:          0x26  16 47 [ bound X ] 
pyffi.mopp:DEBUG: 216:          0x11  145 110 [ branch Y -> 220: 221: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 220:            0x41  [ triangle 17 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 221:            0x40  [ triangle 16 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 222:          0x27  110 218 [ bound Y ] 
pyffi.mopp:DEBUG: 225:          0x09  70 70 [ triangle offset += 70, offset is now 70 ] 
pyffi.mopp:DEBUG: 227:          0x11  207 192 [ branch Y -> 231: 246: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 231:            0x26  0 43 [ bound X ] 
pyffi.mopp:DEBUG: 234:            0x13  142 136 [ branch ? -> 238: 242: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 238:              0x26  16 43 [ bound X ] 
pyffi.mopp:DEBUG: 241:              0x4F  [ triangle 101 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 242:              0x27  148 207 [ bound Y ] 
pyffi.mopp:DEBUG: 245:              0x30  [ triangle 70 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 246:            0x31  [ triangle 71 ] 
pyffi.mopp:DEBUG:           else: 
pyffi.mopp:DEBUG: 247:        0x11  145 138 [ branch Y -> 251: 265: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 251:          0x28  0 57 [ bound Z ] 
pyffi.mopp:DEBUG: 254:          0x17  95 91 [ branch ? -> 258: 263: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 258:            0x26  43 104 [ bound X ] 
pyffi.mopp:DEBUG: 261:            0x50  93 [ triangle 93 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 263:            0x50  53 [ triangle 53 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 265:          0x12  90 70 [ branch Z -> 269: 312: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 269:            0x12  42 19 [ branch Z -> 273: 293: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 273:              0x27  138 195 [ bound Y ] 
pyffi.mopp:DEBUG: 276:              0x09  52 52 [ triangle offset += 52, offset is now 52 ] 
pyffi.mopp:DEBUG: 278:              0x17  132 128 [ branch ? -> 282: 286: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 282:                0x27  138 176 [ bound Y ] 
pyffi.mopp:DEBUG: 285:                0x30  [ triangle 52 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 286:                0x28  0 25 [ bound Z ] 
pyffi.mopp:DEBUG: 289:                0x26  84 135 [ bound X ] 
pyffi.mopp:DEBUG: 292:                0x3B  [ triangle 63 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 293:              0x10  103 84 [ branch X -> 297: 304: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 297:                0x12  72 39 [ branch Z -> 301: 303: ] 
pyffi.mopp:DEBUG:                     if: 
pyffi.mopp:DEBUG: 301:                  0x50  51 [ triangle 51 ] 
pyffi.mopp:DEBUG:                     else: 
pyffi.mopp:DEBUG: 303:                  0x3F  [ triangle 15 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 304:                0x28  19 72 [ bound Z ] 
pyffi.mopp:DEBUG: 307:                0x27  174 231 [ bound Y ] 
pyffi.mopp:DEBUG: 310:                0x50  50 [ triangle 50 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 312:            0x27  192 242 [ bound Y ] 
pyffi.mopp:DEBUG: 315:            0x11  231 216 [ branch Y -> 319: 326: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 319:              0x28  70 121 [ bound Z ] 
pyffi.mopp:DEBUG: 322:              0x26  40 103 [ bound X ] 
pyffi.mopp:DEBUG: 325:              0x3E  [ triangle 14 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 326:              0x26  60 132 [ bound X ] 
pyffi.mopp:DEBUG: 329:              0x3D  [ triangle 13 ] 
pyffi.mopp:DEBUG:         else: 
pyffi.mopp:DEBUG: 330:      0x10  199 174 [ branch X -> 334: 420: ] 
pyffi.mopp:DEBUG:           if: 
pyffi.mopp:DEBUG: 334:        0x11  141 132 [ branch Y -> 338: 352: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 338:          0x28  0 19 [ bound Z ] 
pyffi.mopp:DEBUG: 341:          0x26  102 183 [ bound X ] 
pyffi.mopp:DEBUG: 344:          0x12  11 5 [ branch Z -> 348: 350: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 348:            0x50  54 [ triangle 54 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 350:            0x50  55 [ triangle 55 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 352:          0x11  197 192 [ branch Y -> 356: 376: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 356:            0x28  0 47 [ bound Z ] 
pyffi.mopp:DEBUG: 359:            0x17  165 153 [ branch ? -> 363: 371: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 363:              0x28  0 22 [ bound Z ] 
pyffi.mopp:DEBUG: 366:              0x26  117 177 [ bound X ] 
pyffi.mopp:DEBUG: 369:              0x50  62 [ triangle 62 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 371:              0x26  133 199 [ bound X ] 
pyffi.mopp:DEBUG: 374:              0x50  61 [ triangle 61 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 376:            0x11  231 223 [ branch Y -> 380: 409: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 380:              0x28  19 113 [ bound Z ] 
pyffi.mopp:DEBUG: 383:              0x18  99 96 [ branch ? -> 387: 395: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 387:                0x28  19 72 [ bound Z ] 
pyffi.mopp:DEBUG: 390:                0x26  100 167 [ bound X ] 
pyffi.mopp:DEBUG: 393:                0x50  49 [ triangle 49 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 395:                0x26  133 199 [ bound X ] 
pyffi.mopp:DEBUG: 398:                0x12  68 44 [ branch Z -> 402: 404: ] 
pyffi.mopp:DEBUG:                     if: 
pyffi.mopp:DEBUG: 402:                  0x50  48 [ triangle 48 ] 
pyffi.mopp:DEBUG:                     else: 
pyffi.mopp:DEBUG: 404:                  0x26  164 199 [ bound X ] 
pyffi.mopp:DEBUG: 407:                  0x50  47 [ triangle 47 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 409:              0x28  66 145 [ bound Z ] 
pyffi.mopp:DEBUG: 412:              0x10  167 130 [ branch X -> 416: 418: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 416:                0x50  95 [ triangle 95 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 418:                0x50  94 [ triangle 94 ] 
pyffi.mopp:DEBUG:           else: 
pyffi.mopp:DEBUG: 420:        0x27  79 226 [ bound Y ] 
pyffi.mopp:DEBUG: 423:        0x12  71 44 [ branch Z -> 427: 471: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 427:          0x27  79 197 [ bound Y ] 
pyffi.mopp:DEBUG: 430:          0x26  174 235 [ bound X ] 
pyffi.mopp:DEBUG: 433:          0x09  56 56 [ triangle offset += 56, offset is now 56 ] 
pyffi.mopp:DEBUG: 435:          0x10  235 216 [ branch X -> 439: 464: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 439:            0x11  135 132 [ branch Y -> 443: 452: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 443:              0x12  35 16 [ branch Z -> 447: 451: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 447:                0x26  174 219 [ bound X ] 
pyffi.mopp:DEBUG: 450:                0x30  [ triangle 56 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 451:                0x31  [ triangle 57 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 452:              0x12  47 32 [ branch Z -> 456: 460: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 456:                0x26  174 219 [ bound X ] 
pyffi.mopp:DEBUG: 459:                0x34  [ triangle 60 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 460:                0x26  197 235 [ bound X ] 
pyffi.mopp:DEBUG: 463:                0x33  [ triangle 59 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 464:            0x28  32 71 [ bound Z ] 
pyffi.mopp:DEBUG: 467:            0x27  89 174 [ bound Y ] 
pyffi.mopp:DEBUG: 470:            0x32  [ triangle 58 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 471:          0x11  177 171 [ branch Y -> 475: 513: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 475:            0x28  59 144 [ bound Z ] 
pyffi.mopp:DEBUG: 478:            0x26  232 255 [ bound X ] 
pyffi.mopp:DEBUG: 481:            0x13  122 111 [ branch ? -> 485: 499: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 485:              0x14  144 138 [ branch ? -> 489: 494: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 489:                0x27  89 132 [ bound Y ] 
pyffi.mopp:DEBUG: 492:                0x50  41 [ triangle 41 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 494:                0x28  59 109 [ bound Z ] 
pyffi.mopp:DEBUG: 497:                0x50  40 [ triangle 40 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 499:              0x14  145 138 [ branch ? -> 503: 508: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 503:                0x28  106 144 [ bound Z ] 
pyffi.mopp:DEBUG: 506:                0x50  100 [ triangle 100 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 508:                0x27  129 177 [ bound Y ] 
pyffi.mopp:DEBUG: 511:                0x50  39 [ triangle 39 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 513:            0x26  195 243 [ bound X ] 
pyffi.mopp:DEBUG: 516:            0x09  38 38 [ triangle offset += 38, offset is now 38 ] 
pyffi.mopp:DEBUG: 518:            0x15  155 151 [ branch ? -> 522: 526: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 522:              0x28  44 113 [ bound Z ] 
pyffi.mopp:DEBUG: 525:              0x38  [ triangle 46 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 526:              0x28  69 144 [ bound Z ] 
pyffi.mopp:DEBUG: 529:              0x30  [ triangle 38 ] 
pyffi.mopp:DEBUG:     else: 
pyffi.mopp:DEBUG:  27:  0x10  167 123 [ branch X -> 31: 38: ] 
pyffi.mopp:DEBUG:       if: 
pyffi.mopp:DEBUG:  31:    0x24  119 108 [ branch ? -> 530: 671: ] 
pyffi.mopp:DEBUG:         if: 
pyffi.mopp:DEBUG: 530:      0x26  16 167 [ bound X ] 
pyffi.mopp:DEBUG: 533:      0x12  207 185 [ branch Z -> 537: 608: ] 
pyffi.mopp:DEBUG:           if: 
pyffi.mopp:DEBUG: 537:        0x10  88 78 [ branch X -> 541: 574: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 541:          0x28  102 194 [ bound Z ] 
pyffi.mopp:DEBUG: 544:          0x27  16 119 [ bound Y ] 
pyffi.mopp:DEBUG: 547:          0x09  67 67 [ triangle offset += 67, offset is now 67 ] 
pyffi.mopp:DEBUG: 549:          0x11  79 69 [ branch Y -> 553: 562: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 553:            0x28  139 194 [ bound Z ] 
pyffi.mopp:DEBUG: 556:            0x13  107 101 [ branch ? -> 560: 561: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 560:              0x36  [ triangle 73 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 561:              0x37  [ triangle 74 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 562:            0x26  16 62 [ bound X ] 
pyffi.mopp:DEBUG: 565:            0x10  42 31 [ branch X -> 569: 570: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 569:              0x30  [ triangle 67 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 570:              0x28  139 194 [ bound Z ] 
pyffi.mopp:DEBUG: 573:              0x38  [ triangle 75 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 574:          0x27  0 22 [ bound Y ] 
pyffi.mopp:DEBUG: 577:          0x12  157 146 [ branch Z -> 581: 582: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 581:            0x31  [ triangle 1 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 582:            0x12  207 182 [ branch Z -> 586: 607: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 586:              0x15  158 150 [ branch ? -> 590: 603: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 590:                0x28  146 187 [ bound Z ] 
pyffi.mopp:DEBUG: 593:                0x16  98 94 [ branch ? -> 597: 602: ] 
pyffi.mopp:DEBUG:                     if: 
pyffi.mopp:DEBUG: 597:                  0x26  78 121 [ bound X ] 
pyffi.mopp:DEBUG: 600:                  0x50  72 [ triangle 72 ] 
pyffi.mopp:DEBUG:                     else: 
pyffi.mopp:DEBUG: 602:                  0x32  [ triangle 2 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 603:                0x26  118 167 [ bound X ] 
pyffi.mopp:DEBUG: 606:                0x33  [ triangle 3 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 607:              0x34  [ triangle 4 ] 
pyffi.mopp:DEBUG:           else: 
pyffi.mopp:DEBUG: 608:        0x27  16 119 [ bound Y ] 
pyffi.mopp:DEBUG: 611:        0x26  39 167 [ bound X ] 
pyffi.mopp:DEBUG: 614:        0x10  66 59 [ branch X -> 618: 625: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 618:          0x28  185 233 [ bound Z ] 
pyffi.mopp:DEBUG: 621:          0x27  77 119 [ bound Y ] 
pyffi.mopp:DEBUG: 624:          0x38  [ triangle 8 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 625:          0x11  79 52 [ branch Y -> 629: 647: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 629:            0x28  185 211 [ bound Z ] 
pyffi.mopp:DEBUG: 632:            0x18  164 157 [ branch ? -> 636: 640: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 636:              0x26  59 125 [ bound X ] 
pyffi.mopp:DEBUG: 639:              0x36  [ triangle 6 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 640:              0x27  16 55 [ bound Y ] 
pyffi.mopp:DEBUG: 643:              0x26  78 167 [ bound X ] 
pyffi.mopp:DEBUG: 646:              0x35  [ triangle 5 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 647:            0x26  59 143 [ bound X ] 
pyffi.mopp:DEBUG: 650:            0x10  125 105 [ branch X -> 654: 667: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 654:              0x28  191 233 [ bound Z ] 
pyffi.mopp:DEBUG: 657:              0x17  90 86 [ branch ? -> 661: 662: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 661:                0x37  [ triangle 7 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 662:                0x28  208 233 [ bound Z ] 
pyffi.mopp:DEBUG: 665:                0x50  97 [ triangle 97 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 667:              0x28  208 254 [ bound Z ] 
pyffi.mopp:DEBUG: 670:              0x4E  [ triangle 30 ] 
pyffi.mopp:DEBUG:         else: 
pyffi.mopp:DEBUG: 671:      0x26  0 152 [ bound X ] 
pyffi.mopp:DEBUG: 674:      0x10  63 39 [ branch X -> 678: 717: ] 
pyffi.mopp:DEBUG:           if: 
pyffi.mopp:DEBUG: 678:        0x28  102 188 [ bound Z ] 
pyffi.mopp:DEBUG: 681:        0x27  110 218 [ bound Y ] 
pyffi.mopp:DEBUG: 684:        0x09  68 68 [ triangle offset += 68, offset is now 68 ] 
pyffi.mopp:DEBUG: 686:        0x11  207 200 [ branch Y -> 690: 713: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 690:          0x26  0 52 [ bound X ] 
pyffi.mopp:DEBUG: 693:          0x17  84 78 [ branch ? -> 697: 704: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 697:            0x27  110 151 [ bound Y ] 
pyffi.mopp:DEBUG: 700:            0x26  16 42 [ bound X ] 
pyffi.mopp:DEBUG: 703:            0x30  [ triangle 68 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 704:            0x28  118 188 [ bound Z ] 
pyffi.mopp:DEBUG: 707:            0x13  164 151 [ branch ? -> 711: 712: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 711:              0x31  [ triangle 69 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 712:              0x4E  [ triangle 98 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 713:          0x28  118 160 [ bound Z ] 
pyffi.mopp:DEBUG: 716:          0x4F  [ triangle 99 ] 
pyffi.mopp:DEBUG:           else: 
pyffi.mopp:DEBUG: 717:        0x11  203 176 [ branch Y -> 721: 774: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 721:          0x28  158 254 [ bound Z ] 
pyffi.mopp:DEBUG: 724:          0x12  233 220 [ branch Z -> 728: 767: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 728:            0x10  107 85 [ branch X -> 732: 759: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 732:              0x12  209 185 [ branch Z -> 736: 740: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 736:                0x26  39 87 [ bound X ] 
pyffi.mopp:DEBUG: 739:                0x3A  [ triangle 10 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 740:                0x27  108 187 [ bound Y ] 
pyffi.mopp:DEBUG: 743:                0x15  150 146 [ branch ? -> 747: 751: ] 
pyffi.mopp:DEBUG:                     if: 
pyffi.mopp:DEBUG: 747:                  0x26  39 87 [ bound X ] 
pyffi.mopp:DEBUG: 750:                  0x39  [ triangle 9 ] 
pyffi.mopp:DEBUG:                     else: 
pyffi.mopp:DEBUG: 751:                  0x28  206 233 [ bound Z ] 
pyffi.mopp:DEBUG: 754:                  0x26  64 107 [ bound X ] 
pyffi.mopp:DEBUG: 757:                  0x50  96 [ triangle 96 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 759:              0x28  206 233 [ bound Z ] 
pyffi.mopp:DEBUG: 762:              0x27  115 187 [ bound Y ] 
pyffi.mopp:DEBUG: 765:              0x50  32 [ triangle 32 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 767:            0x27  112 179 [ bound Y ] 
pyffi.mopp:DEBUG: 770:            0x26  105 152 [ bound X ] 
pyffi.mopp:DEBUG: 773:            0x4F  [ triangle 31 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 774:          0x28  118 222 [ bound Z ] 
pyffi.mopp:DEBUG: 777:          0x09  11 11 [ triangle offset += 11, offset is now 11 ] 
pyffi.mopp:DEBUG: 779:          0x12  160 142 [ branch Z -> 783: 790: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 783:            0x27  200 242 [ bound Y ] 
pyffi.mopp:DEBUG: 786:            0x26  50 132 [ bound X ] 
pyffi.mopp:DEBUG: 789:            0x31  [ triangle 12 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 790:            0x15  148 136 [ branch ? -> 794: 798: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 794:              0x26  50 132 [ bound X ] 
pyffi.mopp:DEBUG: 797:              0x30  [ triangle 11 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 798:              0x26  85 152 [ bound X ] 
pyffi.mopp:DEBUG: 801:              0x1B  122 117 [ branch ? -> 805: 806: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 805:                0x47  [ triangle 34 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 806:                0x28  175 222 [ bound Z ] 
pyffi.mopp:DEBUG: 809:                0x27  176 226 [ bound Y ] 
pyffi.mopp:DEBUG: 812:                0x46  [ triangle 33 ] 
pyffi.mopp:DEBUG:       else: 
pyffi.mopp:DEBUG:  38:    0x27  7 242 [ bound Y ] 
pyffi.mopp:DEBUG:  41:    0x24  179 147 [ branch ? -> 813: 953: ] 
pyffi.mopp:DEBUG:         if: 
pyffi.mopp:DEBUG: 813:      0x12  226 208 [ branch Z -> 817: 937: ] 
pyffi.mopp:DEBUG:           if: 
pyffi.mopp:DEBUG: 817:        0x10  227 209 [ branch X -> 821: 905: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 821:          0x12  167 155 [ branch Z -> 825: 840: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 825:            0x27  7 52 [ bound Y ] 
pyffi.mopp:DEBUG: 828:            0x26  155 217 [ bound X ] 
pyffi.mopp:DEBUG: 831:            0x15  158 155 [ branch ? -> 835: 839: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 835:              0x27  7 34 [ bound Y ] 
pyffi.mopp:DEBUG: 838:              0x48  [ triangle 24 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 839:              0x49  [ triangle 25 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 840:            0x11  55 46 [ branch Y -> 844: 866: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 844:              0x28  155 211 [ bound Z ] 
pyffi.mopp:DEBUG: 847:              0x09  26 26 [ triangle offset += 26, offset is now 26 ] 
pyffi.mopp:DEBUG: 849:              0x10  187 157 [ branch X -> 853: 857: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 853:                0x28  196 211 [ bound Z ] 
pyffi.mopp:DEBUG: 856:                0x43  [ triangle 45 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 857:                0x14  58 51 [ branch ? -> 861: 865: ] 
pyffi.mopp:DEBUG:                     if: 
pyffi.mopp:DEBUG: 861:                  0x26  157 187 [ bound X ] 
pyffi.mopp:DEBUG: 864:                  0x42  [ triangle 44 ] 
pyffi.mopp:DEBUG:                     else: 
pyffi.mopp:DEBUG: 865:                  0x30  [ triangle 26 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 866:              0x18  168 162 [ branch ? -> 870: 881: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 870:                0x28  195 226 [ bound Z ] 
pyffi.mopp:DEBUG: 873:                0x27  105 179 [ bound Y ] 
pyffi.mopp:DEBUG: 876:                0x26  149 227 [ bound X ] 
pyffi.mopp:DEBUG: 879:                0x50  86 [ triangle 86 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG: 881:                0x27  46 150 [ bound Y ] 
pyffi.mopp:DEBUG: 884:                0x10  187 184 [ branch X -> 888: 895: ] 
pyffi.mopp:DEBUG:                     if: 
pyffi.mopp:DEBUG: 888:                  0x28  196 226 [ bound Z ] 
pyffi.mopp:DEBUG: 891:                  0x27  46 107 [ bound Y ] 
pyffi.mopp:DEBUG: 894:                  0x4C  [ triangle 28 ] 
pyffi.mopp:DEBUG:                     else: 
pyffi.mopp:DEBUG: 895:                  0x14  71 67 [ branch ? -> 899: 903: ] 
pyffi.mopp:DEBUG:                       if: 
pyffi.mopp:DEBUG: 899:                    0x27  46 107 [ bound Y ] 
pyffi.mopp:DEBUG: 902:                    0x4B  [ triangle 27 ] 
pyffi.mopp:DEBUG:                       else: 
pyffi.mopp:DEBUG: 903:                    0x50  85 [ triangle 85 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 905:          0x15  192 190 [ branch ? -> 909: 917: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 909:            0x28  102 167 [ bound Z ] 
pyffi.mopp:DEBUG: 912:            0x27  31 94 [ bound Y ] 
pyffi.mopp:DEBUG: 915:            0x50  43 [ triangle 43 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG: 917:            0x28  131 198 [ bound Z ] 
pyffi.mopp:DEBUG: 920:            0x26  214 251 [ bound X ] 
pyffi.mopp:DEBUG: 923:            0x14  109 103 [ branch ? -> 927: 932: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 927:              0x27  49 150 [ bound Y ] 
pyffi.mopp:DEBUG: 930:              0x50  76 [ triangle 76 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 932:              0x27  91 177 [ bound Y ] 
pyffi.mopp:DEBUG: 935:              0x50  77 [ triangle 77 ] 
pyffi.mopp:DEBUG:           else: 
pyffi.mopp:DEBUG: 937:        0x27  52 179 [ bound Y ] 
pyffi.mopp:DEBUG: 940:        0x26  123 186 [ bound X ] 
pyffi.mopp:DEBUG: 943:        0x11  114 105 [ branch Y -> 947: 948: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 947:          0x4D  [ triangle 29 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 948:          0x26  140 186 [ bound X ] 
pyffi.mopp:DEBUG: 951:          0x50  87 [ triangle 87 ] 
pyffi.mopp:DEBUG:         else: 
pyffi.mopp:DEBUG: 953:      0x28  110 222 [ bound Z ] 
pyffi.mopp:DEBUG: 956:      0x26  130 247 [ bound X ] 
pyffi.mopp:DEBUG: 959:      0x12  156 142 [ branch Z -> 963: 977: ] 
pyffi.mopp:DEBUG:           if: 
pyffi.mopp:DEBUG: 963:        0x10  207 195 [ branch X -> 967: 972: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 967:          0x27  211 242 [ bound Y ] 
pyffi.mopp:DEBUG: 970:          0x50  36 [ triangle 36 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG: 972:          0x27  174 226 [ bound Y ] 
pyffi.mopp:DEBUG: 975:          0x50  37 [ triangle 37 ] 
pyffi.mopp:DEBUG:           else: 
pyffi.mopp:DEBUG: 977:        0x11  226 211 [ branch Y -> 981: 1044: ] 
pyffi.mopp:DEBUG:             if: 
pyffi.mopp:DEBUG: 981:          0x09  78 78 [ triangle offset += 78, offset is now 78 ] 
pyffi.mopp:DEBUG: 983:          0x12  198 175 [ branch Z -> 987: 1015: ] 
pyffi.mopp:DEBUG:               if: 
pyffi.mopp:DEBUG: 987:            0x10  207 183 [ branch X -> 991: 995: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG: 991:              0x27  196 226 [ bound Y ] 
pyffi.mopp:DEBUG: 994:              0x33  [ triangle 81 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG: 995:              0x11  200 174 [ branch Y -> 999: 1003: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG: 999:                0x26  225 247 [ bound X ] 
pyffi.mopp:DEBUG:1002:                0x30  [ triangle 78 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG:1003:                0x16  158 152 [ branch ? -> 1007: 1011: ] 
pyffi.mopp:DEBUG:                     if: 
pyffi.mopp:DEBUG:1007:                  0x27  196 214 [ bound Y ] 
pyffi.mopp:DEBUG:1010:                  0x32  [ triangle 80 ] 
pyffi.mopp:DEBUG:                     else: 
pyffi.mopp:DEBUG:1011:                  0x26  204 247 [ bound X ] 
pyffi.mopp:DEBUG:1014:                  0x31  [ triangle 79 ] 
pyffi.mopp:DEBUG:               else: 
pyffi.mopp:DEBUG:1015:            0x17  192 186 [ branch ? -> 1019: 1034: ] 
pyffi.mopp:DEBUG:                 if: 
pyffi.mopp:DEBUG:1019:              0x26  145 227 [ bound X ] 
pyffi.mopp:DEBUG:1022:              0x11  199 176 [ branch Y -> 1026: 1030: ] 
pyffi.mopp:DEBUG:                   if: 
pyffi.mopp:DEBUG:1026:                0x28  194 222 [ bound Z ] 
pyffi.mopp:DEBUG:1029:                0x36  [ triangle 84 ] 
pyffi.mopp:DEBUG:                   else: 
pyffi.mopp:DEBUG:1030:                0x26  145 186 [ bound X ] 
pyffi.mopp:DEBUG:1033:                0x34  [ triangle 82 ] 
pyffi.mopp:DEBUG:                 else: 
pyffi.mopp:DEBUG:1034:              0x28  186 198 [ bound Z ] 
pyffi.mopp:DEBUG:1037:              0x27  147 200 [ bound Y ] 
pyffi.mopp:DEBUG:1040:              0x26  183 247 [ bound X ] 
pyffi.mopp:DEBUG:1043:              0x35  [ triangle 83 ] 
pyffi.mopp:DEBUG:             else: 
pyffi.mopp:DEBUG:1044:          0x28  142 178 [ bound Z ] 
pyffi.mopp:DEBUG:1047:          0x26  130 207 [ bound X ] 
pyffi.mopp:DEBUG:1050:          0x50  35 [ triangle 35 ] 
pyffi.toaster:INFO:Finished.

The modify_disableparallax spell
--------------------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "--dry-run", "modify_disableparallax", nif_dir + "test_fix_disableparallax.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_disableparallax.nif ===
pyffi.toaster:INFO:  --- modify_disableparallax ---
pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
pyffi.toaster:INFO:      ~~~ NiTriStrips [Sphere] ~~~
pyffi.toaster:INFO:        ~~~ NiTexturingProperty [] ~~~
pyffi.toaster:INFO:      ~~~ NiTriStrips [Sphere 2] ~~~
pyffi.toaster:INFO:        ~~~ NiTexturingProperty [] ~~~
pyffi.toaster:INFO:          disabling parallax shader
pyffi.toaster:INFO:  writing to temporary file
pyffi.toaster:INFO:Finished.

The dump_pixeldata spell
------------------------

XXX Todo: find an open source nif which can be used for testing.

The check_tangentspace spell
----------------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "check_tangentspace", nif_dir + "test_check_tangentspace1.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_check_tangentspace1.nif ===
pyffi.toaster:INFO:  --- check_tangentspace ---
pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
pyffi.toaster:INFO:      ~~~ NiTriStrips [Plane] ~~~
pyffi.toaster:INFO:        checking tangent space
pyffi.toaster:INFO:Finished.
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "check_tangentspace", nif_dir + "test_check_tangentspace2.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_check_tangentspace2.nif ===
pyffi.toaster:INFO:  --- check_tangentspace ---
pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
pyffi.toaster:INFO:      ~~~ NiTriStrips [Plane] ~~~
pyffi.toaster:INFO:        checking tangent space
pyffi.toaster:INFO:Finished.
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "check_tangentspace", nif_dir + "test_check_tangentspace3.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
ValueError: tangent space data has invalid size, expected 96 bytes but got 95
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "check_tangentspace", nif_dir + "test_check_tangentspace4.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_check_tangentspace4.nif ===
pyffi.toaster:INFO:  --- check_tangentspace ---
pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
pyffi.toaster:INFO:      ~~~ NiTriStrips [Plane] ~~~
pyffi.toaster:INFO:        checking tangent space
pyffi.toaster:WARNING:non-unit tangent [ 123.000 456.000 789.000 ] ...
pyffi.toaster:WARNING:non-ortogonal tangent space at vertex 0
pyffi.toaster:WARNING:...
pyffi.toaster:WARNING:...
pyffi.toaster:WARNING:...
pyffi.toaster:WARNING:...
pyffi.toaster:WARNING:calculated tangent space differs from original at vertex 0
pyffi.toaster:WARNING:old: [0.0, 0.0, 1.0]
pyffi.toaster:WARNING:old: [123.0, 456.0, 789.0]
pyffi.toaster:WARNING:old: [1.0, 0.0, 0.0]
pyffi.toaster:WARNING:new: [0.0, 0.0, 1.0]
pyffi.toaster:WARNING:new: ...
pyffi.toaster:WARNING:new: ...
pyffi.toaster:INFO:Finished.

The check_tristrip spell
------------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "check_tristrip", nif_dir + "test_opt_dupverts.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_dupverts.nif ===
pyffi.toaster:INFO:  --- check_tristrip ---
pyffi.toaster:INFO:    ~~~ NiNode [Lowerclass Dunmer Cup Type-1] ~~~
pyffi.toaster:INFO:      ~~~ NiTriStrips [Lowerclass Dunmer Cup Type-1] ~~~
pyffi.toaster:INFO:        ~~~ NiTriStripsData [] ~~~
pyffi.toaster:INFO:          getting triangles
pyffi.toaster:INFO:          checking strip triangles
pyffi.toaster:INFO:          stitched strip length = 1247
pyffi.toaster:INFO:          num stitches          = 617
pyffi.toaster:INFO:          checking unstitched strip triangles
pyffi.toaster:INFO:          restitching
pyffi.toaster:INFO:          stitched strip length = 919
pyffi.toaster:INFO:          num stitches          = 289
pyffi.toaster:INFO:          checking restitched strip triangles
pyffi.toaster:INFO:          num strips            = 208
pyffi.toaster:INFO:          average strip length  = 3.029
pyffi.toaster:INFO:          recalculating strips
pyffi.toaster:INFO:          checking strip triangles
pyffi.toaster:INFO:          num strips            = 120
pyffi.toaster:INFO:          average strip length  = 3.808
pyffi.toaster:INFO:          checking stitched strip triangles
pyffi.toaster:INFO:          checking unstitched strip triangles
pyffi.toaster:INFO:average strip length = 3.808333
pyffi.toaster:INFO:Finished.

The fix_mergeskeletonroots spell
--------------------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=2", "--raise", "--dry-run", "fix_mergeskeletonroots", nif_dir + "test_fix_mergeskeletonroots.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_mergeskeletonroots.nif ===
pyffi.nif.data:DEBUG:Reading header at 0x00000000
pyffi.nif.data:DEBUG:Version 0x14000005
pyffi.nif.data:DEBUG:Reading NiNode block at 0x000000D4
pyffi.nif.data:DEBUG:Reading NiNode block at 0x00000134
pyffi.nif.data:DEBUG:Reading NiTriStrips block at 0x0000019A
pyffi.nif.data:DEBUG:Reading NiStencilProperty block at 0x000001F7
pyffi.nif.data:DEBUG:Reading NiTriStripsData block at 0x00000220
pyffi.nif.data:DEBUG:Reading NiSkinInstance block at 0x00000324
pyffi.nif.data:DEBUG:Reading NiSkinData block at 0x00000338
pyffi.nif.data:DEBUG:Reading NiSkinPartition block at 0x000003FF
pyffi.nif.data:DEBUG:Reading NiTriStrips block at 0x00000567
pyffi.nif.data:DEBUG:Reading NiTriStripsData block at 0x000005C2
pyffi.nif.data:DEBUG:Reading NiSkinInstance block at 0x00000676
pyffi.nif.data:DEBUG:Reading NiSkinData block at 0x0000068A
pyffi.nif.data:DEBUG:Reading NiSkinPartition block at 0x00000739
pyffi.nif.data:DEBUG:Reading NiNode block at 0x00000829
pyffi.toaster:INFO:  --- fix_mergeskeletonroots ---
pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
pyffi.nif.ninode:DEBUG:detaching Sphere from Armature
pyffi.nif.ninode:DEBUG:attaching Sphere to Scene Root
pyffi.toaster:INFO:      reassigned skeleton root of Sphere
pyffi.toaster:INFO:  writing to temporary file
pyffi.nif.data:DEBUG:Writing header
pyffi.nif.data:DEBUG:Writing NiNode block
pyffi.nif.data:DEBUG:Writing NiNode block
pyffi.nif.data:DEBUG:Writing NiTriStrips block
pyffi.nif.data:DEBUG:Writing NiStencilProperty block
pyffi.nif.data:DEBUG:Writing NiTriStripsData block
pyffi.nif.data:DEBUG:Writing NiSkinInstance block
pyffi.nif.data:DEBUG:Writing NiSkinData block
pyffi.nif.data:DEBUG:Writing NiSkinPartition block
pyffi.nif.data:DEBUG:Writing NiNode block
pyffi.nif.data:DEBUG:Writing NiTriStrips block
pyffi.nif.data:DEBUG:Writing NiTriStripsData block
pyffi.nif.data:DEBUG:Writing NiSkinInstance block
pyffi.nif.data:DEBUG:Writing NiSkinData block
pyffi.nif.data:DEBUG:Writing NiSkinPartition block
pyffi.toaster:INFO:Finished.

The fix_scale spell
-------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "--dry-run", "fix_scale", nif_dir + "test_opt_dupverts.nif", "-a", "10"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_dupverts.nif ===
pyffi.toaster:INFO:  --- fix_scale ---
pyffi.toaster:INFO:    scaling by factor 10.000000
pyffi.toaster:INFO:    ~~~ NiNode [Lowerclass Dunmer Cup Type-1] ~~~
pyffi.toaster:INFO:      ~~~ BSXFlags [BSX] ~~~
pyffi.toaster:INFO:      ~~~ NiStringExtraData [UPB] ~~~
pyffi.toaster:INFO:      ~~~ bhkCollisionObject [] ~~~
pyffi.toaster:INFO:        ~~~ bhkRigidBody [] ~~~
pyffi.toaster:INFO:          ~~~ bhkListShape [] ~~~
pyffi.toaster:INFO:            ~~~ bhkTransformShape [] ~~~
pyffi.toaster:INFO:              ~~~ bhkBoxShape [] ~~~
pyffi.toaster:INFO:            ~~~ bhkTransformShape [] ~~~
pyffi.toaster:INFO:              ~~~ bhkBoxShape [] ~~~
pyffi.toaster:INFO:            ~~~ bhkTransformShape [] ~~~
pyffi.toaster:INFO:              ~~~ bhkBoxShape [] ~~~
pyffi.toaster:INFO:            ~~~ bhkTransformShape [] ~~~
pyffi.toaster:INFO:              ~~~ bhkBoxShape [] ~~~
pyffi.toaster:INFO:            ~~~ bhkTransformShape [] ~~~
pyffi.toaster:INFO:              ~~~ bhkBoxShape [] ~~~
pyffi.toaster:INFO:            ~~~ bhkTransformShape [] ~~~
pyffi.toaster:INFO:              ~~~ bhkBoxShape [] ~~~
pyffi.toaster:INFO:            ~~~ bhkTransformShape [] ~~~
pyffi.toaster:INFO:              ~~~ bhkBoxShape [] ~~~
pyffi.toaster:INFO:      ~~~ NiTriStrips [Lowerclass Dunmer Cup Type-1] ~~~
pyffi.toaster:INFO:        ~~~ NiBinaryExtraData [Tangent space (binormal & tangent vectors)] ~~~
pyffi.toaster:INFO:        ~~~ NiMaterialProperty [WoodInteriorPlain] ~~~
pyffi.toaster:INFO:        ~~~ NiTexturingProperty [] ~~~
pyffi.toaster:INFO:          ~~~ NiSourceTexture [] ~~~
pyffi.toaster:INFO:        ~~~ NiTriStripsData [] ~~~
pyffi.toaster:INFO:  writing to temporary file
pyffi.toaster:INFO:Finished.

The fix_mopp spell
------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=1", "--raise", "--dry-run", "fix_mopp", nif_dir + "test_mopp.nif"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS
pyffi.toaster:INFO:=== tests/formats/nif/test_mopp.nif ===
pyffi.toaster:INFO:  --- fix_mopp ---
pyffi.toaster:INFO:    ~~~ NiNode [Scene Root] ~~~
pyffi.toaster:INFO:      ~~~ bhkCollisionObject [] ~~~
pyffi.toaster:INFO:        ~~~ bhkRigidBody [] ~~~
pyffi.toaster:INFO:          ~~~ bhkMoppBvTreeShape [] ~~~
pyffi.toaster:INFO:            updating mopp
Mopper. Copyright (c) 2008, NIF File Format Library and Tools.
All rights reserved.
<BLANKLINE>
Options:
  --help      for usage help
  --license   for licensing details
<BLANKLINE>
Mopper uses havok. Copyright 1999-2008 Havok.com Inc. (and its Licensors).
All Rights Reserved. See www.havok.com for details.
<BLANKLINE>
<BLANKLINE>
pyffi.toaster:INFO:  writing to temporary file
pyffi.toaster:INFO:Finished.

The check_version spell
-----------------------

>>> import sys
>>> sys.path.append("scripts/nif")
>>> import niftoaster
>>> sys.argv = ["niftoaster.py", "--verbose=1", "check_version", "tests/spells/nif", "-a", "10"]
>>> niftoaster.NifToaster().cli() # doctest: +ELLIPSIS +REPORT_NDIFF
pyffi.toaster:INFO:=== tests/formats/nif/invalid.nif ===
pyffi.toaster:ERROR:TEST FAILED ON tests/formats/nif/invalid.nif
pyffi.toaster:ERROR:If you were running a spell that came with PyFFI, then
pyffi.toaster:ERROR:please report this as a bug (include the file) on
pyffi.toaster:ERROR:https://github.com/niftools/pyffi/issues
pyffi.toaster:INFO:=== tests/formats/nif/nds.nif ===
pyffi.toaster:INFO:  version      0x14020008
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/neosteam.nif ===
pyffi.toaster:INFO:  version      0x0A010000
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test.nif ===
pyffi.toaster:INFO:  version      0x14010003
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_centerradius.nif ===
pyffi.toaster:INFO:  version      0x14010003
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_check_tangentspace1.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_check_tangentspace2.nif ===
pyffi.toaster:INFO:  version      0x14020007
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 34
pyffi.toaster:INFO:=== tests/formats/nif/test_check_tangentspace3.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_check_tangentspace4.nif ===
pyffi.toaster:INFO:  version      0x14020007
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 34
pyffi.toaster:INFO:=== tests/formats/nif/test_convexverticesshape.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_dump_tex.nif ===
pyffi.toaster:INFO:  version      0x14010003
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_clampmaterialalpha.nif ===
pyffi.toaster:INFO:  version      0x0A000100
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_cleanstringpalette.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_detachhavoktristripsdata.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_disableparallax.nif ===
pyffi.toaster:INFO:  version      0x14000004
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_ffvt3rskinpartition.nif ===
pyffi.toaster:INFO:  version      0x0A010000
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_mergeskeletonroots.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_tangentspace.nif ===
pyffi.toaster:INFO:  version      0x14000004
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_fix_texturepath.nif ===
pyffi.toaster:INFO:  version      0x14000004
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_grid_128x128.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_grid_64x64.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_mopp.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_collision_complex_mopp.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_collision_mopp.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_collision_packed.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_collision_to_boxshape.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_collision_to_boxshape_notabox.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_collision_unpacked.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_delunusedbones.nif ===
pyffi.toaster:INFO:  version      0x0A010000
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_dupgeomdata.nif ===
pyffi.toaster:INFO:  version      0x04000002
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_dupverts.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_emptyproperties.nif ===
pyffi.toaster:INFO:  version      0x0A000100
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_grid_layout.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_mergeduplicates.nif ===
pyffi.toaster:INFO:  version      0x14000004
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_vertex_cache.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:=== tests/formats/nif/test_opt_zeroscale.nif ===
pyffi.toaster:INFO:  version      0x0A000100
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_skincenterradius.nif ===
pyffi.toaster:INFO:  version      0x0A010000
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:  user version 0
pyffi.toaster:INFO:=== tests/formats/nif/test_vertexcolor.nif ===
pyffi.toaster:INFO:  version      0x14000005
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:  user version 11
pyffi.toaster:INFO:version 0x0A010000
pyffi.toaster:INFO:  number of nifs: 4
pyffi.toaster:INFO:  user version:  [0]
pyffi.toaster:INFO:  user version2: [0]
pyffi.toaster:INFO:version 0x0A000100
pyffi.toaster:INFO:  number of nifs: 3
pyffi.toaster:INFO:  user version:  [0]
pyffi.toaster:INFO:  user version2: [0]
pyffi.toaster:INFO:version 0x04000002
pyffi.toaster:INFO:  number of nifs: 1
pyffi.toaster:INFO:  user version:  [0]
pyffi.toaster:INFO:  user version2: [0]
pyffi.toaster:INFO:version 0x14010003
pyffi.toaster:INFO:  number of nifs: 3
pyffi.toaster:INFO:  user version:  [0]
pyffi.toaster:INFO:  user version2: [0]
pyffi.toaster:INFO:version 0x14000004
pyffi.toaster:INFO:  number of nifs: 4
pyffi.toaster:INFO:  user version:  [0]
pyffi.toaster:INFO:  user version2: [0]
pyffi.toaster:INFO:version 0x14000005
pyffi.toaster:INFO:  number of nifs: 19
pyffi.toaster:INFO:  user version:  [11]
pyffi.toaster:INFO:  user version2: [11]
pyffi.toaster:INFO:version 0x14020007
pyffi.toaster:INFO:  number of nifs: 2
pyffi.toaster:INFO:  user version:  [11]
pyffi.toaster:INFO:  user version2: [34]
pyffi.toaster:INFO:version 0x14020008
pyffi.toaster:INFO:  number of nifs: 1
pyffi.toaster:INFO:  user version:  [0]
pyffi.toaster:INFO:  user version2: [0]
pyffi.toaster:INFO:Finished.
"""
