"""Module which contains all spells that fix something in a nif."""

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

class SpellDelTangentSpace(NifSpell):
    """Delete tangentspace if it is present."""

    SPELLNAME = "fix_deltangentspace"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiBinaryExtraData)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # does this block have tangent space data?
            for extra in branch.get_extra_datas():
                if isinstance(extra, NifFormat.NiBinaryExtraData):
                    if (extra.name ==
                        'Tangent space (binormal & tangent vectors)'):
                        self.toaster.msg("removing tangent space block")
                        branch.remove_extra_data(extra)
            # all extra blocks here done; no need to recurse further
            return False
        # recurse further
        return True

class SpellAddTangentSpace(NifSpell):
    """Add tangentspace if none is present."""

    SPELLNAME = "fix_addtangentspace"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiBinaryExtraData)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # does this block have tangent space data?
            for extra in branch.get_extra_datas():
                if isinstance(extra, NifFormat.NiBinaryExtraData):
                    if (extra.name ==
                        'Tangent space (binormal & tangent vectors)'):
                        # tangent space found, done!
                        return False
            # no tangent space found
            self.toaster.msg("adding tangent space")
            branch.update_tangent_space()
            # all extra blocks here done; no need to recurse further
            return False
        else:
            # recurse further
            return True

class SpellFFVT3RSkinPartition(NifSpell):
    """Create or update skin partition, with settings that work for Freedom
    Force vs. The 3rd Reich."""

    SPELLNAME = "fix_ffvt3rskinpartition"
    READONLY = False

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiSkinInstance)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiTriBasedGeom):
            # if the branch has skinning info
            if branch.skin_instance:
                # then update the skin partition
                self.toaster.msg("updating skin partition")
                branch.update_skin_partition(
                    maxbonesperpartition=4, maxbonespervertex=4,
                    stripify=False, verbose=0, padbones=True)
            return False
            # done; no need to recurse further in this branch
        else:
            # recurse further
            return True

class SpellFixTexturePath(NifSpell):
    """Fix the texture path. Transforms 0x0a into \\n and 0x0d into \\r.
    This fixes a bug in nifs saved with older versions of nifskope.
    Also transforms / into \\. This fixes problems when packing files into
    a bsa archive."""

    SPELLNAME = "fix_texturepath"
    READONLY = False

    def datainspect(self):
        # only run the spell if there are NiSourceTexture blocks
        return self.inspectblocktype(NifFormat.NiSourceTexture)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch, texturing properties and source
        # textures
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiTexturingProperty,
                                   NifFormat.NiSourceTexture))
    
    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiSourceTexture):
            if (('\n'.encode("ascii") in branch.file_name)
                or ('\r'.encode("ascii") in branch.file_name)
                or ('/'.encode("ascii") in branch.file_name)):
                branch.file_name = branch.file_name.replace(
                    '\n'.encode("ascii"),
                    '\\n'.encode("ascii"))
                branch.file_name = branch.file_name.replace(
                    '\r'.encode("ascii"),
                    '\\r'.encode("ascii"))
                branch.file_name = branch.file_name.replace(
                    '/'.encode("ascii"),
                    '\\'.encode("ascii"))
                self.toaster.msg("fixed file name '%s'" % branch.file_name)
            return False
        else:
            return True

# the next spell solves issue #2065018, MiddleWolfRug01.NIF
class SpellDetachHavokTriStripsData(NifSpell):
    """For NiTriStrips if their NiTriStripsData also occurs in a
    bhkNiTriStripsShape, make deep copy of data in havok. This is
    mainly useful as a preperation for other spells that act on
    NiTriStripsData, to ensure that the havok data remains untouched."""

    SPELLNAME = "fix_detachhavoktristripsdata"
    READONLY = False

    def __init__(self, *args, **kwargs):
        NifSpell.__init__(self, *args, **kwargs)
        # provides the bhknitristripsshapes within the current NiTriStrips
        self.bhknitristripsshapes = None

    def datainspect(self):
        # only run the spell if there are bhkNiTriStripsShape blocks
        return self.inspectblocktype(NifFormat.bhkNiTriStripsShape)

    def dataentry(self):
        # build list of all NiTriStrips blocks
        self.nitristrips = [branch for branch in self.data.get_global_iterator()
                            if isinstance(branch, NifFormat.NiTriStrips)]
        if self.nitristrips:
            return True
        else:
            return False

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch and collision branch
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.bhkCollisionObject,
                                   NifFormat.bhkRefObject))
    
    def branchentry(self, branch):
        if isinstance(branch, NifFormat.bhkNiTriStripsShape):
            for i, data in enumerate(branch.strips_data):
                if data in [otherbranch.data
                            for otherbranch in self.nitristrips]:
                        # detach!
                        self.toaster.msg("detaching havok data")
                        branch.strips_data[i] = NifFormat.NiTriStripsData().deepcopy(data)
            return False
        else:
            return True

class SpellClampMaterialAlpha(NifSpell):
    """Clamp corrupted material alpha values."""

    SPELLNAME = "fix_clampmaterialalpha"
    READONLY = False

    def datainspect(self):
        # only run the spell if there are material property blocks
        return self.inspectblocktype(NifFormat.NiMaterialProperty)

    def branchinspect(self, branch):
        # only inspect the NiAVObject branch, and material properties
        return isinstance(branch, (NifFormat.NiAVObject,
                                   NifFormat.NiMaterialProperty))
    
    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiMaterialProperty):
            # check if alpha exceeds usual values
            if branch.alpha > 1:
                # too large
                self.toaster.msg(
                    "clamping alpha value (%f -> 1.0)" % branch.alpha)
                branch.alpha = 1.0
            elif branch.alpha < 0:
                # too small
                self.toaster.msg(
                    "clamping alpha value (%f -> 0.0)" % branch.alpha)
                branch.alpha = 0.0
            # stop recursion
            return False
        else:
            # keep recursing into children
            return True

class SpellSendGeometriesToBindPosition(pyffi.spells.nif.SpellVisitSkeletonRoots):
    """Transform skinned geometries so similar bones have the same bone data,
    and hence, the same bind position, over all geometries.
    """
    SPELLNAME = "fix_sendgeometriestobindposition"
    READONLY = False

    def skelrootentry(self, branch):
        self.toaster.msg("sending geometries to bind position")
        branch.send_geometries_to_bind_position()

class SpellSendDetachedGeometriesToNodePosition(pyffi.spells.nif.SpellVisitSkeletonRoots):
    """Transform geometries so each set of geometries that shares bones
    is aligned with the transform of the root bone of that set.
    """
    SPELLNAME = "fix_senddetachedgeometriestonodeposition"
    READONLY = False

    def skelrootentry(self, branch):
        self.toaster.msg("sending detached geometries to node position")
        branch.send_detached_geometries_to_node_position()

class SpellSendBonesToBindPosition(pyffi.spells.nif.SpellVisitSkeletonRoots):
    """Transform bones so bone data agrees with bone transforms,
    and hence, all bones are in bind position.
    """
    SPELLNAME = "fix_sendbonestobindposition"
    READONLY = False

    def skelrootentry(self, branch):
        self.toaster.msg("sending bones to bind position")
        branch.send_bones_to_bind_position()

class SpellMergeSkeletonRoots(NifSpell):
    """Merges skeleton roots in the nif file so that no skeleton root has
    another skeleton root as child. Warns if merge is impossible (this happens
    if the global skin data of the geometry is not the unit transform).
    """
    SPELLNAME = "fix_mergeskeletonroots"
    READONLY = False

    def datainspect(self):
        # only run the spell if there are skinned geometries
        return self.inspectblocktype(NifFormat.NiSkinInstance)

    def dataentry(self):
        # make list of skeleton roots
        skelroots = []
        for branch in self.data.get_global_iterator():
            if isinstance(branch, NifFormat.NiGeometry):
                if branch.skin_instance:
                    skelroot = branch.skin_instance.skeleton_root
                    if skelroot and not skelroot in skelroots:
                        skelroots.append(skelroot)
        # find the 'root' skeleton roots (those that have no other skeleton
        # roots as child)
        self.skelrootlist = set()
        for skelroot in skelroots:
            for skelroot_other in skelroots:
                if skelroot_other is skelroot:
                    continue
                if skelroot_other.find_chain(skelroot):
                    # skelroot_other has skelroot as child
                    # so skelroot is no longer an option
                    break
            else:
                # no skeleton root children!
                self.skelrootlist.add(skelroot)
        # only apply spell if there are skeleton roots
        if self.skelrootlist:
            return True
        else:
            return False

    def branchinspect(self, branch):
        # only inspect the NiNode branch
        return isinstance(branch, NifFormat.NiNode)
    
    def branchentry(self, branch):
        if branch in self.skelrootlist:
            result, failed = branch.merge_skeleton_roots()
            for geom in result:
                self.toaster.msg("reassigned skeleton root of %s" % geom.name)
            self.skelrootlist.remove(branch)
        # continue recursion only if there is still more to come
        if self.skelrootlist:
            return True
        else:
            return False

class SpellApplySkinDeformation(NifSpell):
    """Apply skin deformation to nif."""
    # TODO
    pass

class SpellStrip(NifSpell):
    """Delete blocks that match the exclude list."""

    SPELLNAME = "fix_strip"
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
        if not self.toaster.isadmissiblebranchtype(branch.__class__):
            # it is, wipe it out
            self.toaster.msg("stripping this branch")
            self.data.replace_global_node(branch, None)
            # do not recurse further
            return False
        else:
            # this one was not excluded, keep recursing
            return True

class SpellDisableParallax(NifSpell):
    """Disable parallax shader (for Oblivion, but may work on other nifs too).
    """

    SPELLNAME = "fix_disableparallax"
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

class SpellScale(NifSpell):
    """Scale a model."""

    SPELLNAME = "fix_scale"
    READONLY = False

    @classmethod
    def toastentry(cls, toaster):
        if not toaster.options["arg"]:
            toaster.logger.warn(
                "must specify scale as argument (e.g. -a 10) "
                "to apply spell")
            return False
        else:
            toaster.scale = float(toaster.options["arg"])
            return True

    def dataentry(self):
        # initialize list of blocks that have been scaled
        self.toaster.msg("scaling by factor %f" % self.toaster.scale)
        self.scaled_branches = []
        return True

    def branchinspect(self, branch):
        # only do every branch once
        return (branch not in self.scaled_branches)

    def branchentry(self, branch):
        branch.apply_scale(self.toaster.scale)
        self.scaled_branches.append(branch)
        # continue recursion
        return True

class SpellFixCenterRadius(pyffi.spells.nif.check.SpellCheckCenterRadius):
    """Recalculate geometry centers and radii."""
    SPELLNAME = "fix_centerradius"
    READONLY = False

class SpellFixSkinCenterRadius(pyffi.spells.nif.check.SpellCheckSkinCenterRadius):
    """Recalculate skin centers and radii."""
    SPELLNAME = "fix_skincenterradius"
    READONLY = False

class SpellFixMopp(pyffi.spells.nif.check.SpellCheckMopp):
    """Recalculate mopp data from collision geometry."""
    SPELLNAME = "fix_mopp"
    READONLY = False

    def branchentry(self, branch):
        # we don't recycle the check mopp code here
        # that spell does not actually recalculate the mopp at all
        # it only parses the existing mopp...
        if not isinstance(branch, NifFormat.bhkMoppBvTreeShape):
            # keep recursing
            return True
        else:
            self.toaster.msg("updating mopp")
            branch.update_mopp()
