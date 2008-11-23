"""Module which contains all spells that check something in a nif file."""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, NIF File Format Library and Tools.
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

from __future__ import with_statement
from contextlib import closing
from itertools import izip
import tempfile

from PyFFI.Formats.NIF import NifFormat
from PyFFI.Spells.NIF import NifSpell

class SpellReadWrite(NifSpell):
    """Like the original read-write spell, but with additional file size
    check."""

    SPELLNAME = "check_readwrite"

    def dataentry(self):
        self.toaster.msgblockbegin("writing to temporary file")

        f_tmp = tempfile.TemporaryFile()
        try:
            self.data.write(f_tmp)
            # comparing the files will usually be different because
            # blocks may have been written back in a different order,
            # so cheaply just compare file sizes
            self.toaster.msg("comparing file sizes")
            self.stream.seek(0, 2)
            f_tmp.seek(0, 2)
            if self.stream.tell() != f_tmp.tell():
                self.toaster.msg("original size: %i" % self.stream.tell())
                self.toaster.msg("written size:  %i" % f_tmp.tell())
                f_tmp.seek(0)
                f_debug = open("debug.nif", "wb")
                f_debug.write(f_tmp.read(-1))
                f_debug.close()
                raise StandardError('write check failed: file sizes differ (written file saved as debug.nif for inspection)')
        finally:
            f_tmp.close()
    
        self.toaster.msgblockend()

        # spell is finished: prevent recursing into the tree
        return False

class SpellNodeNamesByFlag(NifSpell):
    """This spell goes over all nif files, and at the end, it gives a summary
    of which node names where used with particular flags."""

    SPELLNAME = "check_nodenamesbyflag"

    @classmethod
    def toastentry(cls, toaster):
        toaster.flagdict = {}
        return True

    @classmethod
    def toastexit(cls, toaster):
        for flag, names in toaster.flagdict.iteritems():
            self.toaster.msg("%s %s" % (flag, names))

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiNode)

    def branchinspect(self, branch):
        # stick to main tree
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if isinstance(branch, NifFormat.NiAVObject):
            if not branch.flags in self.toaster.flagdict:
                self.toaster.flagdict[branch.flags] = []
            if not branch.name in self.toaster.flagdict[branch.flags]:
                self.toaster.flagdict[branch.flags].append(branch.name)
            return True
        else:
            return False

class SpellCompareSkinData(NifSpell):
    """This spell compares skinning data with a reference nif."""

    SPELLNAME = "check_compareskindata"

    # helper functions (to compare with custom tolerance)

    @staticmethod
    def are_vectors_equal(oldvec, newvec, tolerance=0.01):
        return (max([abs(x-y)
                for (x,y) in izip(oldvec.asList(), newvec.asList())])
                < tolerance)

    @staticmethod
    def are_matrices_equal(oldmat, newmat, tolerance=0.01):
        return (max([max([abs(x-y)
                     for (x,y) in izip(oldrow, newrow)])
                    for (oldrow, newrow) in izip(oldmat.asList(),
                                                 newmat.asList())])
                < tolerance)

    @staticmethod
    def are_floats_equal(oldfloat, newfloat, tolerance=0.01):
        return abs(oldfloat - newfloat) < tolerance

    @classmethod
    def toastentry(cls, toaster):
        """Read reference nif file given as argument."""
        # if no argument given, do not apply spell
        if not toaster.options.get("arg"):
            return False
        # read reference nif
        toaster.refdata = NifFormat.Data()
        with closing(open(toaster.options["arg"], "rb")) as reffile:
            toaster.refdata.read(reffile)
        # find bone data in reference nif
        toaster.refbonedata = []
        for refgeom in toaster.refdata.getGlobalTreeIterator():
            if (isinstance(refgeom, NifFormat.NiGeometry)
                and refgeom.skinInstance and refgeom.skinInstance.data):
                toaster.refbonedata += zip(refgeom.skinInstance.bones,
                                           refgeom.skinInstance.data.boneList)
        # only apply spell if the reference nif has bone data
        return bool(toaster.refbonedata)

    def datainspect(self):
        return self.inspectblocktype(NifFormat.NiSkinData)

    def branchinspect(self, branch):
        # stick to main tree
        return isinstance(branch, NifFormat.NiAVObject)

    def branchentry(self, branch):
        if (isinstance(branch, NifFormat.NiGeometry)
            and branch.skinInstance and branch.skinInstance.data):
            for bonenode, bonedata in izip(branch.skinInstance.bones,
                                           branch.skinInstance.data.boneList):
                for refbonenode, refbonedata in self.toaster.refbonedata:
                    if bonenode.name == refbonenode.name:
                        self.toaster.msg("checking bone %s" % bonenode.name)
                        # compare
                        if not self.are_matrices_equal(refbonedata.rotation,
                                                       bonedata.rotation):
                            #raise ValueError(
                            self.toaster.msg(
                                "rotation mismatch\n%s\n!=\n%s\n"
                                % (refbonedata.rotation, bonedata.rotation))
                        if not self.are_vectors_equal(refbonedata.translation,
                                                      bonedata.translation):
                            #raise ValueError(
                            self.toaster.msg(
                                "translation mismatch\n%s\n!=\n%s\n"
                                % (refbonedata.translation,
                                   bonedata.translation))
                        if not self.are_floats_equal(refbonedata.scale,
                                                     bonedata.scale):
                            #raise ValueError(
                            self.toaster.msg(
                                "scale mismatch %s != %s"
                                % (refbonedata.scale, bonedata.scale))
            # stop in this branch
            return False
        else:
            # keep iterating
            return True
