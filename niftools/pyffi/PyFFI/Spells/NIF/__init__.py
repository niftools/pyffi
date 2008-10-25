import PyFFI.Spells
import PyFFI.Formats.NIF

# import all spells

import checkbhkbodycenter
import checkcenterradius
import checkconvexshape
import checkmopp
import checkskincenterradius
import checkskinpartition
import checktangentspace
import checktristrip
import disableparallax
import dump
import exportpixeldata
import ffvt3rskinpartition
import fix_addtangentspace
import fix_deltangentspace
import fix_detachhavoktristripsdata
import fix_texturepath
import hackcheckskindata
import hackmultiskelroot
import hackskindataidtransform
import hackskinrestpose
import mergeskelandrestpos
import optimize
import optimize_split
import read
import readwrite
import scale
import texdump
import updatecenterradius
import updatemopp
import updateskinpartition


class NifSpell(PyFFI.Spells.Spell):
    """Base class for spells for nif files."""
    pass

class NifToaster(PyFFI.Spells.Toaster):
    """Base class for toasting nif files."""
    FILEFORMAT = PyFFI.Formats.NIF.NifFormat
    SPELLS = [
        checkbhkbodycenter,
        checkcenterradius,
        checkconvexshape,
        checkmopp,
        checkskincenterradius,
        checkskinpartition,
        checktangentspace,
        checktristrip,
        disableparallax,
        dump,
        exportpixeldata,
        ffvt3rskinpartition,
        fix_addtangentspace,
        fix_deltangentspace,
        fix_detachhavoktristripsdata,
        fix_texturepath,
        hackcheckskindata,
        hackmultiskelroot,
        hackskindataidtransform,
        hackskinrestpose,
        mergeskelandrestpos,
        optimize,
        optimize_split,
        read,
        readwrite,
        scale,
        texdump,
        updatecenterradius,
        updatemopp,
        updateskinpartition]

