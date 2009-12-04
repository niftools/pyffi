"""Module which contains all spells that modify a nif (anything that
is not a fix).
"""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, NIF File Format Library and Tools.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the NIF File Format Library and Tools
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****
# --------------------------------------------------------------------------

from pyffi.formats.nif import NifFormat
from pyffi.spells.nif import NifSpell
import pyffi.spells.nif
import pyffi.spells.nif.check # recycle checking spells for update spells
import os

class SpellTexturePath(NifSpell):
    """Changes the texture path while keeping the texture names."""

    SPELLNAME = "modify_texturepath"
    READONLY = False

    @classmethod
    def toastentry(cls, toaster):
        if not toaster.options["arg"]:
            toaster.logger.warn(
                "must specify path as argument "
                "(e.g. -a textures\\pm\\dungeons\\bloodyayleid\\interior) "
                "to apply spell")
            return False
        else:
            toaster.texture_path = str(toaster.options["arg"])
            # standardize the path
            toaster.texture_path = toaster.texture_path.replace("/", os.sep)
            toaster.texture_path = toaster.texture_path.replace("\\", os.sep)
            return True

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiSourceTexture)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTexturingProperty,
                                   NifFormat.NiSourceTexture))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiSourceTexture):
            old_file_name = str(branch.file_name) # for reporting
            # note: replace backslashes by os.sep in filename, and
            # when joined, revert them back, for linux
            branch.file_name = os.path.join(
                self.toaster.texture_path,
                os.path.basename(old_file_name.replace("\\", os.sep))
                ).replace(os.sep, "\\") 
            self.toaster.msg("%s -> %s" % (old_file_name, branch.file_name))
            # all textures done no need to recurse further.
            return False
        else:
            # recurse further
            return True

class SpellCollisionType(NifSpell):
    """Sets the object collision to be a different type"""

    SPELLNAME = "modify_collisiontype"
    READONLY = False

    class CollisionTypeStatic:
        layer = 1
        motion_system = 7
        unknown_byte1 = 1
        unknown_byte2 = 1
        quality_type = 1
        wind = 0
        solid = True
        mass = 0

    class CollisionTypeAnimStatic(CollisionTypeStatic):
        layer = 2
        motion_system = 6
        unknown_byte1 = 2
        unknown_byte2 = 2
        quality_type = 2

    class CollisionTypeClutter(CollisionTypeAnimStatic):
        layer = 4
        motion_system = 4
        quality_type = 3
        mass = 10

    class CollisionTypeWeapon(CollisionTypeClutter):
        layer = 5
        mass = 25
		
    class CollisionTypeNonCollidable(CollisionTypeStatic):
        """Same as static except that nothing collides with it."""
        layer = 15

    COLLISION_TYPE_DICT = {
        "static": CollisionTypeStatic,
        "anim_static": CollisionTypeAnimStatic,
        "clutter": CollisionTypeClutter,
        "weapon": CollisionTypeWeapon,
        "non_collidable": CollisionTypeNonCollidable
        }

    @classmethod
    def toastentry(cls, toaster):
        try:
            toaster.col_type = cls.COLLISION_TYPE_DICT[toaster.options["arg"]]
        except KeyError:
            # incorrect arg
            toaster.logger.warn(
                "must specify collision type to change to as argument "
                "(e.g. -a static (accepted names: %s) "
                "to apply spell"
                % ", ".join(cls.COLLISION_TYPE_DICT.iterkeys()))
            return False
        else:
            return True

    def datainspect(self):
        return self.inspectblocktype(NifFormat.bhkRigidBody)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.bhkCollisionObject,
                                   NifFormat.bhkRigidBody,
                                   NifFormat.bhkMoppBvTreeShape,
                                   NifFormat.bhkPackedNiTriStripsShape))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.bhkRigidBody):
            branch.layer = self.toaster.col_type.layer
            branch.layer_copy = self.toaster.col_type.layer
            branch.mass = self.toaster.col_type.mass
            branch.motion_system = self.toaster.col_type.motion_system
            branch.unknown_byte_1 = self.toaster.col_type.unknown_byte1
            branch.unknown_byte_2 = self.toaster.col_type.unknown_byte2
            branch.quality_type = self.toaster.col_type.quality_type
            branch.wind = self.toaster.col_type.wind
            branch.solid = self.toaster.col_type.solid
            self.toaster.msg("collision set to %s" % self.toaster.options["arg"])
            # bhkPackedNiTriStripsShape could be further down, so keep looking
            return True
        elif isinstance(branch, NifFormat.bhkPackedNiTriStripsShape):
            for subshape in branch.sub_shapes:
                subshape.layer = self.toaster.col_type.layer
            self.toaster.msg("collision set to %s" % self.toaster.options["arg"])
            # all extra blocks here done; no need to recurse further
            return False
        else:
            # recurse further
            return True

class SpellScaleAnimationTime(NifSpell):
    """Scales the animation time."""
    # XXX only scales NiTransformData (no controllers, or other data)

    SPELLNAME = "modify_scaleanimationtime"
    READONLY = False
    
    @classmethod
    def toastentry(cls, toaster):
        if not toaster.options["arg"]:
            toaster.logger.warn(
                "must specify scaling number as argument "
                "(e.g. -a 0.6) to apply spell")
            return False
        else:
            toaster.animation_scale = float(toaster.options["arg"])
            return True

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiTransformData)

    def branchinspect(self, branch):
        # inspect the NiAVObject branch, and NiControllerSequence
        # branch (for kf files)
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiControllerManager,
                                   NifFormat.NiControllerSequence,
                                   NifFormat.NiTransformController,
                                   NifFormat.NiTransformInterpolator,
                                   NifFormat.NiTransformData))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTransformData):
            if branch.rotation_type == 4:
                for key in branch.xyz_rotations[0].keys:
                    key.time *= self.toaster.animation_scale
                for key in branch.xyz_rotations[1].keys:
                    key.time *= self.toaster.animation_scale
                for key in branch.xyz_rotations[2].keys:
                    key.time *= self.toaster.animation_scale
            else:
                for key in branch.quaternion_keys:
                    key.time *= self.toaster.animation_scale
            for key in branch.translations.keys:
                key.time *= self.toaster.animation_scale
            for key in branch.scales.keys:
                key.time *= self.toaster.animation_scale
            # no children of NiTransformData so no need to recurse further.
            return False
        if isinstance(branch, NifFormat.NiControllerSequence):
            branch.stop_time *= self.toaster.animation_scale
            # probably children of NiControllerSequence so need to recurse further.
            return True
        else:
            # recurse further
            return True
