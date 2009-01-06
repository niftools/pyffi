"""Custom functions for NiObject."""

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

def find(self, block_name = None, block_type = None):
    # does this block match the search criteria?
    if block_name and block_type:
        if isinstance(self, block_type):
            try:
                if block_name == self.name: return self
            except AttributeError:
                pass
    elif block_name:
        try:
            if block_name == self.name: return self
        except AttributeError:
            pass
    elif block_type:
        if isinstance(self, block_type): return self

    # ok, this block is not a match, so check further down in tree
    for child in self.getRefs():
        blk = child.find(block_name, block_type)
        if blk: return blk

    return None



def findChain(self, block, block_type = None):
    """Finds a chain of blocks going from C{self} to C{block}. If found,
    self is the first element and block is the last element. If no branch
    found, returns an empty list. Does not check whether there is more
    than one branch; if so, the first one found is returned.

    @param block: The block to find a chain to.
    @param block_type: The type that blocks should have in this chain."""

    if self is block: return [self]
    for child in self.getRefs():
        if block_type and not isinstance(child, block_type): continue
        child_chain = child.findChain(block, block_type)
        if child_chain:
            return [self] + child_chain

    return []

def applyScale(self, scale):
    """Propagate scale down the hierarchy.
    Override this method if it contains geometry data that can be scaled.
    If overridden, call this base method to propagate scale down the hierarchy."""
    for child in self.getRefs():
        child.applyScale(scale)

def tree(self, block_type = None, follow_all = True, unique = False):
    """A generator for parsing all blocks in the tree (starting from and
    including C{self}).

    @param block_type: If not C{None}, yield only blocks of the type C{block_type}.
    @param follow_all: If C{block_type} is not C{None}, then if this is C{True} the function will parse the whole tree. Otherwise, the function will not follow branches that start by a non-C{block_type} block.

    @param unique: Whether the generator can return the same block twice or not."""
    # unique blocks: reduce this to the case of non-unique blocks
    if unique:
        block_list = []
        for block in self.tree(block_type = block_type, follow_all = follow_all, unique = False):
            if not block in block_list:
                yield block
                block_list.append(block)
        return

    # yield self
    if not block_type:
        yield self
    elif isinstance(self, block_type):
        yield self
    elif not follow_all:
        return # don't recurse further

    # yield tree attached to each child
    for child in self.getRefs():
        for block in child.tree(block_type = block_type, follow_all = follow_all):
            yield block

def _validateTree(self):
    """Raises ValueError if there is a cycle in the tree."""
    # If the tree is parsed, then each block should be visited once.
    # However, as soon as some cycle is present, parsing the tree
    # will visit some child more than once (and as a consequence, infinitely
    # many times). So, walk the reference tree and check that every block is
    # only visited once.
    children = []
    for child in self.tree():
        if child in children:
            raise ValueError('cyclic references detected')
        children.append(child)

def isInterchangeable(self, other):
    """Are the two blocks interchangeable?

    @todo: Rely on AnyType, SimpleType, ComplexType, etc. implementation.
    """
    if isinstance(self, (self.cls.NiProperty, self.cls.NiSourceTexture)):
        # use hash for properties and source textures
        return ((self.__class__ is other.__class__)
                and (self.getHash() == other.getHash()))
    else:
        # for blocks with references: quick check only
        return self is other

