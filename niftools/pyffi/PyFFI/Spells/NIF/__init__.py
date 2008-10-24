import PyFFI.Spells

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

