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
        return self.inspectblocktype(NifFormat.NiObject) #returns more than needed but only way to ensure catches all types of animations

    def branchinspect(self, branch):
        # inspect the NiAVObject branch, and NiControllerSequence
        # branch (for kf files)
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiControllerManager,
                                   NifFormat.NiControllerSequence,
                                   NifFormat.NiTransformController,
                                   NifFormat.NiTransformInterpolator,
                                   NifFormat.NiTransformData,
                                   NifFormat.NiTextKeyExtraData,
                                   NifFormat.NiTimeController,
                                   NifFormat.NiFloatInterpolator,
                                   NifFormat.NiFloatData))

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
            # no children of NiTransformData so no need to recurse
            # further
            return False
        elif isinstance(branch, NifFormat.NiControllerSequence):
            branch.stop_time *= self.toaster.animation_scale
            # recurse further into children of NiControllerSequence
            return True
        elif isinstance(branch, NifFormat.NiTextKeyExtraData):
            for key in branch.text_keys:
                key.time *= self.toaster.animation_scale
            # no children of NiTextKeyExtraData so no need to recurse
            # further
            return False
        elif isinstance(branch, NifFormat.NiTimeController):
            branch.stop_time *= self.toaster.animation_scale
            # recurse further into children of NiTimeController
            return True
        elif isinstance(branch, NifFormat.NiFloatData):
            for key in branch.data.keys:
                key.time *= self.toaster.animation_scale
            # No children of NiFloatData so no need to recurse further.
            return False
        else:
            # recurse further
            return True

class SpellReverseAnimation(NifSpell):
    """Reverses the animation by reversing datas in relation to the time."""

    SPELLNAME = "modify_reverseanimation"
    READONLY = False

    def datainspect(self):
        #returns more than needed but only way to ensure catches all types of animations.
        return self.inspectblocktype(NifFormat.NiObject) 

    def branchinspect(self, branch):
        # inspect the NiAVObject branch, and NiControllerSequence
        # branch (for kf files)
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiControllerManager,
                                   NifFormat.NiControllerSequence,
                                   NifFormat.NiTransformController,
                                   NifFormat.NiTransformInterpolator,
                                   NifFormat.NiTransformData,
                                   NifFormat.NiTextKeyExtraData,
                                   NifFormat.NiTimeController,
                                   NifFormat.NiFloatInterpolator,
                                   NifFormat.NiFloatData))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTransformData):
            if branch.rotation_type == 4:
                key_new_values = reversed([key.value for key in branch.xyz_rotations[0].keys])
                for key, key_new_value in zip(branch.xyz_rotations[0].keys, key_new_values):
                    key.value = key_new_value
                key_new_values = reversed([key.value for key in branch.xyz_rotations[1].keys])
                for key, key_new_value in zip(branch.xyz_rotations[1].keys, key_new_values):
                    key.value = key_new_value
                key_new_values = reversed([key.value for key in branch.xyz_rotations[2].keys])
                for key, key_new_value in zip(branch.xyz_rotations[2].keys, key_new_values):
                    key.value = key_new_value
            else:
                if branch.rotation_type == 3:
                    key_new_values_t = reversed([key.tbc.t for key in branch.quaternion_keys])
                    key_new_values_b = reversed([key.tbc.b for key in branch.quaternion_keys])
                    key_new_values_c = reversed([key.tbc.c for key in branch.quaternion_keys])
                    for key, t, b, c in zip(branch.quaternion_keys, key_new_values_t, key_new_values_b, key_new_values_c):
                        key.tbc.t = t
                        key.tbc.b = b
                        key.tbc.c = c
                else:
                    key_new_values_w = reversed([key.value.w for key in branch.quaternion_keys])
                    key_new_values_x = reversed([key.value.x for key in branch.quaternion_keys])
                    key_new_values_y = reversed([key.value.y for key in branch.quaternion_keys])
                    key_new_values_z = reversed([key.value.z for key in branch.quaternion_keys])
                    for key, w, x, y, z in zip(branch.quaternion_keys, key_new_values_w, key_new_values_x, key_new_values_y, key_new_values_z):
                        key.value.w = w
                        key.value.x = x
                        key.value.y = y
                        key.value.z = z
            key_new_values_x = reversed([key.value.x for key in branch.translations.keys])
            key_new_values_y = reversed([key.value.y for key in branch.translations.keys])
            key_new_values_z = reversed([key.value.z for key in branch.translations.keys])
            for key, x, y, z in zip(branch.translations.keys, key_new_values_x, key_new_values_y, key_new_values_z,):
                key.value.x = x
                key.value.y = y
                key.value.z = z
            key_new_values = reversed([key.value for key in branch.scales.keys])
            for key, key_new_value in zip(branch.scales.keys, key_new_values):
                key.value = key_new_value
            # no children of NiTransformData so no need to recurse further.
            return False
        elif isinstance(branch, NifFormat.NiTextKeyExtraData):
            key_new_values = reversed([key.value for key in branch.text_keys])
            for key, key_new_value in zip(branch.text_keys, key_new_values):
                key.value = key_new_value
            # No children of NiTextKeyExtraData so no need to recurse further.
            return False
        elif isinstance(branch, NifFormat.NiFloatData):
            key_new_values = reversed([key.value for key in branch.data.keys])
            for key, key_new_value in zip(branch.data.keys, key_new_values):
                key.value = key_new_value
            # No children of NiFloatData so no need to recurse further.
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
                "(e.g. -a Stone (accepted names: %s) "
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

class SpellDelVertexColorProperty(NifSpell):
    """Delete vertex color property if it is present."""

    SPELLNAME = "modify_delvertexcolor"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiTriBasedGeom)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                  NifFormat.NiTriBasedGeom,
                                  NifFormat.NiTriBasedGeomData))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # does this block have tangent space data?
            for prop in branch.get_properties():
                if isinstance(prop, NifFormat.NiVertexColorProperty):
                        branch.remove_property(prop)
            # all property blocks here done but not the geometry data so need to recurse further
            return True
        elif isinstance(branch, NifFormat.NiTriBasedGeomData):
            branch.has_vertex_colors = 0
            # no chilren; no need to recurse further
            return False
        # recurse further
        return True

class SpellDelBlocks(NifSpell):
    """Delete blocks that match the exclude list."""

    SPELLNAME = "modify_delblocks"
    READONLY = False

    def _branchinspect(self, branch):
        """This spell inspects every branch, also the non-admissible ones,
        therefore we must override this method.
        """
        return True

    def branchentry(self, branch):
        """Strip branch if it is admissible (as specified by include/exclude
        options of the toaster).
        """
        # check if it is excluded or not
        if not self.toaster.is_admissible_branch_class(branch.__class__):
            # it is, wipe it out
            self.toaster.msg("stripping this branch")
            self.data.replace_global_node(branch, None)
            # do not recurse further
            return False
        else:
            # this one was not excluded, keep recursing
            return True

# identical to niftoaster.py modify_delblocks -x NiAlphaProperty
# delete?
class SpellDelAlphaProperty(NifSpell):
    """Delete alpha property if it is present."""

    SPELLNAME = "modify_delalphaprop"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiTriBasedGeom)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                  NifFormat.NiTriBasedGeom))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # does this block have an Alpha property?
            for prop in branch.get_properties():
                if isinstance(prop, NifFormat.NiAlphaProperty):
                    branch.remove_property(prop)
            # all property blocks here done; no need to recurse further
            return True
        # recurse further
        return True

# identical to niftoaster.py modify_delblocks -x NiSpecularProperty
# delete?
class SpellDelSpecularProperty(NifSpell):
    """Delete specular property if it is present."""

    SPELLNAME = "modify_delspecularprop"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiTriBasedGeom)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                  NifFormat.NiTriBasedGeom))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # does this block have a specular property?
            for prop in branch.get_properties():
                if isinstance(prop, NifFormat.NiSpecularProperty):
                        branch.remove_property(prop)
            # all property blocks here done; no need to recurse further
            return True
        # recurse further
        return True

# identical to niftoaster.py modify_delblocks -x NiBSXFlags
# delete?
class SpellDelBSXextradatas(NifSpell):
    """Delete BSXflags if any are present."""

    SPELLNAME = "modify_delBSXflags"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.BSXFlags)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                  NifFormat.NiNode))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiNode):
            # does this block have BSX Flags?
            for extra in branch.get_extra_datas():
                if isinstance(extra, NifFormat.BSXFlags):
                    branch.remove_extra_data(extra)
            # all extra blocks here done; no need to recurse further
            return False
        # recurse further
        return True
		
# identical to niftoaster.py modify_delblocks -x NiStringExtraData
# delete?
class SpellDelNiStringExtraDatas(NifSpell):
    """Delete NiSringExtraDatas if they are present."""

    SPELLNAME = "modify_delnistringextradatas"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiStringExtraData)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                  NifFormat.NiNode,
                                  NifFormat.NiTriBasedGeom))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiNode):
            # does this block have BSX Flags?
            for extra in branch.get_extra_datas():
                if isinstance(extra, NifFormat.NiStringExtraData):
                    branch.remove_extra_data(extra)
                    self.toaster.msg("NiStringExtraData removed from %s" % (branch.name))
            # all extra blocks here done; no need to recurse further
            return False
        # recurse further
        return True

class SpellDelFleshShapes(NifSpell):
    """Delete any Geometries with a material name of 'skin'"""

    # modify_delskinmaterials?
    SPELLNAME = "modify_delfleshshapes" #not a nice name... maybe rename?
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiMaterialProperty)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTriBasedGeom,
                                   NifFormat.NiMaterialProperty))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiMaterialProperty):
            if branch.name.lower() == "skin":
                self.toaster.msg("stripping this branch")
                self.data.replace_global_node(branch, None)
            # do not recurse further
            return False
        # recurse further
        return True

# identical to niftoaster.py modify_delblocks -x NiCollisionObject
# delete?
class SpellDelCollisionData(NifSpell):
    """Deletes any Collision data present."""

    SPELLNAME = "modify_delcollision"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiNode)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiNode))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiNode):
            if branch.collision_object != None: 
                branch.collision_object = None
                self.toaster.msg("Collision removed from %s" % (branch.name))
            # could have child NiNodes so need to recurse further
            return True
        # recurse further
        return True
		
# identical to niftoaster.py modify_delblocks -x NiTimeController
# delete?
class SpellDelAnimation(NifSpell):
    """Deletes any Animation data present."""

    SPELLNAME = "modify_delanimation"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiNode)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, (NifFormat.NiAVObject))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiAVObject):
            if branch.controller != None: 
                branch.controller = None
                self.toaster.msg("Animation removed from %s" % (branch.name))
            # could have children so need to recurse further
            return True
        elif isinstance(branch, NifFormat.NiNode):
            for child in branch.get_children():
                if isinstance(child, NifFormat.NiTimeController):
                    branch.remove_child(child)
                    self.toaster.msg("Animation removed from %s" % (branch.name))
            
        # recurse further
        return True

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
            if ('lowres'.encode("ascii") not in branch.file_name):
                branch.file_name = branch.file_name.replace(
                    "textures", "textures\\lowres").replace(os.sep, "\\")
                self.toaster.msg("Texture path changed to %s" % (branch.file_name))
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
        return isinstance(branch, (NifFormat.NiAVObject,
                                  NifFormat.NiTriBasedGeom))

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # does this block have an Stencil property?
            for prop in branch.get_properties():
                if isinstance(prop, NifFormat.NiStencilProperty):
                    return False
            # No stencil property found
            self.toaster.msg("adding NiStencilProperty")
            branch.add_property(NifFormat.NiStencilProperty)
			# No geometry children, no need to recurse further
            return False
        # recurse further
        return True

# TODO: implement via modify_delblocks
class SpellMakeFarNif(
    pyffi.spells.SpellGroupSeries(
        pyffi.spells.SpellGroupParallel(
            SpellDelVertexColorProperty,
            SpellDelAlphaProperty,
            SpellDelSpecularProperty,
            SpellDelBSXextradatas,
            SpellDelNiStringExtraDatas,
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
