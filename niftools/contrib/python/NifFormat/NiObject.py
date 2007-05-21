# --------------------------------------------------------------------------
# NifFormat.NiObject
# Custom functions for NiObject.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, NIF File Format Library and Tools.
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
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

def find(self, block_name = None, block_type = None):
    # does this block match the search criteria?
    if block_name != None and block_type != None:
        if isinstance(self, block_type):
            try:
                if block_name == self.name: return self
            except AttributeError:
                pass
    elif block_name != None:
        try:
            if block_name == self.name: return self
        except AttributeError:
            pass
    elif block_type != None:
        if isinstance(self, block_type): return self

    # ok, this block is not a match, so check further down in tree
    for child in self.getRefs():
        blk = child.find(block_name, block_type)
        if blk != None: return blk

    return None

def findChain(self, block):
    """Finds a chain of blocks going from self to <block>. If found,
    self is the first element and block is the last element. If no branch
    found, returns an empty list. Does not check whether there is more
    than one branch; if so, the first one found is returned."""
    if self == block: return [self]
    for child in self.getRefs():
        child_chain = child.findChain(block)
        if child_chain:
            return [self] + child_chain
    return []

def applyScale(self, scale):
    """Propagate scale down the hierarchy.
    Override this method if it contains geometry data that can be scaled.
    If overridden, call this base method to propagate scale down the hierarchy."""
    for child in self.getRefs():
        child.applyScale(scale)

def tree(self):
    """A generator for parsing all blocks in the tree (starting from and
    including self)."""
    # yield self
    yield self

    # yield tree attached to each child
    for child in self.getRefs():
        for block in child.tree():
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
