"""Custom functions for NiNode."""

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

"""
>>> from PyFFI.Formats.NIF import NifFormat
>>> x = NifFormat.NiNode()
>>> y = NifFormat.NiNode()
>>> z = NifFormat.NiNode()
>>> x.numChildren =1
>>> x.children.updateSize()
>>> y in x.children
False
>>> x.children[0] = y
>>> y in x.children
True
>>> x.addChild(z, front = True)
>>> x.addChild(y)
>>> x.numChildren
2
>>> x.children[0] == z
True
>>> x.removeChild(y)
>>> y in x.children
False
>>> x.numChildren
1
>>> e = NifFormat.NiSpotLight()
>>> x.addEffect(e)
>>> x.numEffects
1
>>> e in x.effects
True
"""

def addChild(self, childblock, front = False):
    """Add block to child list."""
    # check if it's already a child
    if childblock in self.children: return
    # increase number of children
    num_children = self.numChildren
    self.numChildren = num_children + 1
    self.children.updateSize()
    # add the child
    if not front:
        self.children[num_children] = childblock
    else:
        for i in xrange(num_children, 0, -1):
            self.children[i] = self.children[i-1]
        self.children[0] = childblock



def removeChild(self, childblock):
    """Remove a block from the child list."""
    children = [child for child in self.children if child != childblock]
    self.numChildren = len(children)
    self.children.updateSize()
    for i, child in enumerate(children):
        self.children[i] = child



def addEffect(self, effectblock):
    """Add an effect to the list of effects."""
    num_effs = self.numEffects
    self.numEffects = num_effs + 1
    self.effects.updateSize()
    self.effects[num_effs] = effectblock

