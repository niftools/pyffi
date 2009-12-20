"""
:mod:`pyffi.spells.nif.modify` ---  spells to make modifications
=================================================================
Module which contains all spells that modify a nif.
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
import pyffi.spells.nif.fix

from itertools import izip
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

    class CollisionTypeTerrain(CollisionTypeStatic):
        layer = 14
        motion_system = 7

    class CollisionTypeClutter(CollisionTypeAnimStatic):
        layer = 4
        motion_system = 4
        quality_type = 3
        mass = 10

    class CollisionTypeWeapon(CollisionTypeClutter):
        layer = 5
        mass = 25
		
    class CollisionTypeNonCollidable(CollisionTypeStatic):
        layer = 15
        motion_system = 7

    COLLISION_TYPE_DICT = {
        "static": CollisionTypeStatic,
        "anim_static": CollisionTypeAnimStatic,
        "clutter": CollisionTypeClutter,
        "weapon": CollisionTypeWeapon,
        "terrain": CollisionTypeTerrain,
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
            self.toaster.msg("collision set to %s"
                             % self.toaster.options["arg"])
            # bhkPackedNiTriStripsShape could be further down, so keep looking
            return True
        elif isinstance(branch, NifFormat.bhkPackedNiTriStripsShape):
            for subshape in branch.sub_shapes:
                subshape.layer = self.toaster.col_type.layer
            self.toaster.msg("collision set to %s"
                             % self.toaster.options["arg"])
            # all extra blocks here done; no need to recurse further
            return False
        else:
            # recurse further
            return True

class SpellScaleAnimationTime(NifSpell):
    """Scales the animation time."""

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
        # returns more than needed but easiest way to ensure it catches all
        # types of animations
        return True

    def branchinspect(self, branch):
        # inspect the NiAVObject branch, and NiControllerSequence
        # branch (for kf files)
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTimeController,
                                   NifFormat.NiInterpolator,
                                   NifFormat.NiControllerManager,
                                   NifFormat.NiControllerSequence,
                                   NifFormat.NiKeyframeData,
                                   NifFormat.NiTextKeyExtraData,
                                   NifFormat.NiFloatData))

    def branchentry(self, branch):

        def scale_key_times(keys):
            """Helper function to scale key times."""
            for key in keys:
                key.time *= self.toaster.animation_scale

        if isinstance(branch, NifFormat.NiKeyframeData):
            if branch.rotation_type == 4:
                scale_key_times(branch.xyz_rotations[0].keys)
                scale_key_times(branch.xyz_rotations[1].keys)
                scale_key_times(branch.xyz_rotations[2].keys)
            else:
                scale_key_times(branch.quaternion_keys)
            scale_key_times(branch.translations.keys)
            scale_key_times(branch.scales.keys)
            # no children of NiKeyframeData so no need to recurse further
            return False
        elif isinstance(branch, NifFormat.NiControllerSequence):
            branch.stop_time *= self.toaster.animation_scale
            # recurse further into children of NiControllerSequence
            return True
        elif isinstance(branch, NifFormat.NiTextKeyExtraData):
            scale_key_times(branch.text_keys)
            # no children of NiTextKeyExtraData so no need to recurse further
            return False
        elif isinstance(branch, NifFormat.NiTimeController):
            branch.stop_time *= self.toaster.animation_scale
            # recurse further into children of NiTimeController
            return True
        elif isinstance(branch, NifFormat.NiFloatData):
            scale_key_times(branch.data.keys)
            # no children of NiFloatData so no need to recurse further
            return False
        else:
            # recurse further
            return True

class SpellReverseAnimation(NifSpell):
    """Reverses the animation by reversing datas in relation to the time."""

    SPELLNAME = "modify_reverseanimation"
    READONLY = False

    def datainspect(self):
        # returns more than needed but easiest way to ensure it catches all
        # types of animations
        return True

    def branchinspect(self, branch):
        # inspect the NiAVObject branch, and NiControllerSequence
        # branch (for kf files)
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTimeController,
                                   NifFormat.NiInterpolator,
                                   NifFormat.NiControllerManager,
                                   NifFormat.NiControllerSequence,
                                   NifFormat.NiKeyframeData,
                                   NifFormat.NiTextKeyExtraData,
                                   NifFormat.NiFloatData))

    def branchentry(self, branch):

        def reverse_keys(keys):
            """Helper function to reverse keys."""
            # copy the values
            key_values = [key.value for key in keys]
            # reverse them
            for key, new_value in izip(keys, reversed(key_values)):
                key.value = new_value

        if isinstance(branch, NifFormat.NiKeyframeData):
            # (this also covers NiTransformData)
            if branch.rotation_type == 4:
                reverse_keys(branch.xyz_rotations[0].keys)
                reverse_keys(branch.xyz_rotations[1].keys)
                reverse_keys(branch.xyz_rotations[2].keys)
            else:
                reverse_keys(branch.quaternion_keys)
            reverse_keys(branch.translations.keys)
            reverse_keys(branch.scales.keys)
            # no children of NiTransformData so no need to recurse further
            return False
        elif isinstance(branch, NifFormat.NiTextKeyExtraData):
            reverse_keys(branch.text_keys)
            # no children of NiTextKeyExtraData so no need to recurse further
            return False
        elif isinstance(branch, NifFormat.NiFloatData):
            reverse_keys(branch.data.keys)
            # no children of NiFloatData so no need to recurse further
            return False
        else:
            # recurse further
            return True

class SpellCollisionMaterial(NifSpell):
    """Sets the object's collision material to be a different type"""

    SPELLNAME = "modify_collisionmaterial"
    READONLY = False

    class CollisionMaterialStone:
        material = 0

    class CollisionMaterialCloth:
        material = 1

    class CollisionMaterialMetal:
        material = 5

    COLLISION_MATERIAL_DICT = {
        "stone": CollisionMaterialStone,
        "cloth": CollisionMaterialCloth,
        "metal": CollisionMaterialMetal
        }

    @classmethod
    def toastentry(cls, toaster):
        try:
            toaster.col_material = cls.COLLISION_MATERIAL_DICT[toaster.options["arg"]]
        except KeyError:
            # incorrect arg
            toaster.logger.warn(
                "must specify collision material to change to as argument "
                "(e.g. -a stone (accepted names: %s) "
                "to apply spell"
                % ", ".join(cls.COLLISION_MATERIAL_DICT.iterkeys()))
            return False
        else:
            return True

    def datainspect(self):
        return self.inspectblocktype(NifFormat.bhkShape)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.bhkCollisionObject,
                                   NifFormat.bhkRigidBody,
                                   NifFormat.bhkShape))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.bhkShape):
            branch.material = self.toaster.col_material.material
            self.toaster.msg("collision material set to %s" % self.toaster.options["arg"])
            # bhkPackedNiTriStripsShape could be further down, so keep looking
            return True
        elif isinstance(branch, NifFormat.bhkPackedNiTriStripsShape) or isinstance(branch, NifFormat.hkPackedNiTriStripsData):
            for subshape in branch.sub_shapes:
                subshape.material = self.toaster.col_type.material
            self.toaster.msg("collision material set to %s" % self.toaster.options["arg"])
            # all extra blocks here done; no need to recurse further
            return False
        else:
            # recurse further
            return True

class SpellDelBranches(NifSpell):
    """Delete blocks that match the exclude list."""

    SPELLNAME = "modify_delbranches"
    READONLY = False

    def is_branch_to_be_deleted(self, branch):
        """Returns ``True`` for those branches that must be deleted.
        The default implementation returns ``True`` for branches that
        are not admissible as specified by include/exclude options of
        the toaster. Override in subclasses that must delete specific
        branches.
        """
        # check if it is excluded or not
        return not self.toaster.is_admissible_branch_class(branch.__class__)

    def _branchinspect(self, branch):
        """This spell inspects every branch, also the non-admissible ones,
        therefore we must override this method.
        """
        return True

    def branchentry(self, branch):
        """Strip branch if it is flagged for deletion.
        """
        # check if it is to be deleted or not
        if self.is_branch_to_be_deleted(branch):
            # it is, wipe it out
            self.toaster.msg("stripping this branch")
            self.data.replace_global_node(branch, None)
            # do not recurse further
            return False
        else:
            # this one was not excluded, keep recursing
            return True

class _SpellDelBranchClasses(SpellDelBranches):
    """Delete blocks that match a given list. Only useful as base class
    for other spells.
    """

    BRANCH_CLASSES_TO_BE_DELETED = ()
    """List of branch classes that have to be deleted."""

    def datainspect(self):
        return any(
            self.inspectblocktype(branch_class)
            for branch_class in self.BRANCH_CLASSES_TO_BE_DELETED)

    def is_branch_to_be_deleted(self, branch):
        return isinstance(branch, self.BRANCH_CLASSES_TO_BE_DELETED)

class SpellDelVertexColor(SpellDelBranches):
    """Delete vertex color properties and vertex color data."""

    SPELLNAME = "modify_delvertexcolor"

    def is_branch_to_be_deleted(self, branch):
        return isinstance(branch, NifFormat.NiVertexColorProperty)

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiTriBasedGeom)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTriBasedGeomData,
                                   NifFormat.NiVertexColorProperty))

    def branchentry(self, branch):
        # delete vertex color property
        SpellDelBranches.branchentry(self, branch)
        # reset vertex color flags
        if isinstance(branch, NifFormat.NiTriBasedGeomData):
            if branch.has_vertex_colors:
                self.toaster.msg("removing vertex colors")
                branch.has_vertex_colors = False
            # no children; no need to recurse further
            return False
        # recurse further
        return True

# identical to niftoaster.py modify_delbranches -x NiAlphaProperty
# delete?
class SpellDelAlphaProperty(_SpellDelBranchClasses):
    """Delete alpha property if it is present."""

    SPELLNAME = "modify_delalphaprop"
    BRANCH_CLASSES_TO_BE_DELETED = (NifFormat.NiAlphaProperty,)

# identical to niftoaster.py modify_delbranches -x NiSpecularProperty
# delete?
class SpellDelSpecularProperty(_SpellDelBranchClasses):
    """Delete specular property if it is present."""

    SPELLNAME = "modify_delspecularprop"
    BRANCH_CLASSES_TO_BE_DELETED = (NifFormat.NiSpecularProperty,)

# identical to niftoaster.py modify_delbranches -x BSXFlags
# delete?
class SpellDelBSXFlags(_SpellDelBranchClasses):
    """Delete BSXFlags if any are present."""

    SPELLNAME = "modify_delbsxflags"
    BRANCH_CLASSES_TO_BE_DELETED = (NifFormat.BSXFlags,)
		
# identical to niftoaster.py modify_delbranches -x NiStringExtraData
# delete?
class SpellDelStringExtraDatas(_SpellDelBranchClasses):
    """Delete NiSringExtraDatas if they are present."""

    SPELLNAME = "modify_delstringextradatas"
    BRANCH_CLASSES_TO_BE_DELETED = (NifFormat.NiStringExtraData,)

class SpellDelFleshShapes(SpellDelBranches):
    """Delete any geometries with a material name of 'skin'"""

    # modify_delskinshapes?
    SPELLNAME = "modify_delfleshshapes" #not a nice name... maybe rename?

    def is_branch_to_be_deleted(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            for prop in branch.get_properties():
                if isinstance(prop, NifFormat.NiMaterialProperty):
                    if prop.name.lower() == "skin":
                        # skin material, delete
                        return True
        # do not delete anything else
        return False

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, NifFormat.NiAVObject)

# identical to niftoaster.py modify_delbranches -x NiCollisionObject
# delete?
class SpellDelCollisionData(_SpellDelBranchClasses):
    """Deletes any Collision data present."""

    SPELLNAME = "modify_delcollision"
    BRANCH_CLASSES_TO_BE_DELETED = (NifFormat.NiCollisionObject,)

# identical to niftoaster.py modify_delbranches -x NiTimeController
# delete?
class SpellDelAnimation(_SpellDelBranchClasses):
    """Deletes any animation data present."""

    SPELLNAME = "modify_delanimation"
    BRANCH_CLASSES_TO_BE_DELETED = (NifFormat.NiTimeController,)

class SpellDisableParallax(NifSpell):
    """Disable parallax shader (for Oblivion, but may work on other nifs too).
    """

    SPELLNAME = "modify_disableparallax"
    READONLY = False

    def datainspect(self):
        # XXX should we check that the nif is Oblivion version?
        # only run the spell if there are textures
        return self.inspectblocktype(NifFormat.NiTexturingProperty)

    def branchinspect(self, branch):
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTexturingProperty))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTexturingProperty):
            # is parallax enabled?
            if branch.apply_mode == 4:
                # yes!
                self.toaster.msg("disabling parallax shader")
                branch.apply_mode = 2
            # stop recursing
            return False
        else:
            # keep recursing
            return True

class SpellLowResTexturePath(NifSpell):
    """Changes the texture path by replacing 'textures/*' with 'textures/lowres/*' - used mainly for making _far.nifs"""

    SPELLNAME = "modify_texturepathlowres"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiSourceTexture)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTexturingProperty,
                                   NifFormat.NiSourceTexture))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiSourceTexture):
            # XXX use (branch.file_name.find('lowres') == -1)?
            if ('lowres'.encode("ascii") not in branch.file_name):
                branch.file_name = branch.file_name.replace(
                    "textures", "textures\\lowres").replace(os.sep, "\\")
                self.toaster.msg("Texture path changed to %s"
                                 % (branch.file_name))
            # all textures done no need to recurse further.
            return False
        else:
            # recurse further
            return True

class SpellAddStencilProperty(NifSpell):
    """Adds a NiStencilProperty to each geometry if it is not present."""

    SPELLNAME = "modify_addstencilprop"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiTriBasedGeom)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # does this block have an stencil property?
            for prop in branch.get_properties():
                if isinstance(prop, NifFormat.NiStencilProperty):
                    return False
            # no stencil property found
            self.toaster.msg("adding NiStencilProperty")
            branch.add_property(NifFormat.NiStencilProperty)
            # no geometry children, no need to recurse further
            return False
        # recurse further
        return True

# TODO: implement via modify_delbranches?
class SpellMakeFarNif(
    pyffi.spells.SpellGroupSeries(
        pyffi.spells.SpellGroupParallel(
            SpellDelVertexColor,
            SpellDelAlphaProperty,
            SpellDelSpecularProperty,
            SpellDelBSXFlags,
            SpellDelStringExtraDatas,
            pyffi.spells.nif.fix.SpellDelTangentSpace,
            SpellDelCollisionData,
            SpellDelAnimation,
            SpellDisableParallax,
            SpellLowResTexturePath),
        pyffi.spells.nif.optimize.SpellOptimize
        )):
    """Spell to make _far type nifs."""
    SPELLNAME = "modify_makefarnif"

class SpellMakeFleshlessNif(
    pyffi.spells.SpellGroupSeries(
        pyffi.spells.SpellGroupParallel(
            SpellDelFleshShapes,
            SpellAddStencilProperty)
        )):
    """Spell to make fleshless CMR (Custom Model Races) clothing type nifs."""
    SPELLNAME = "modify_makefleshlessnif"
