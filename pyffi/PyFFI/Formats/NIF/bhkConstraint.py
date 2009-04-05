"""Custom functions for bhkConstraint."""

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

def getTransformAB(self, parent):
    """Returns the transform of the first entity relative to the second
    entity. Root is simply a nif block that is a common parent to both
    blocks."""
    # check entities
    if self.numEntities != 2:
        raise ValueError("""\
cannot get tranform for constraint that hasn't exactly 2 entities""")
    # find transform of entity A relative to entity B

    # find chains from parent to A and B entities
    chainA = parent.findChain(self.entities[0])
    chainB = parent.findChain(self.entities[1])
    # validate the chains
    assert(isinstance(chainA[-1], self.cls.bhkRigidBody))
    assert(isinstance(chainA[-2], self.cls.NiCollisionObject))
    assert(isinstance(chainA[-3], self.cls.NiNode))
    assert(isinstance(chainB[-1], self.cls.bhkRigidBody))
    assert(isinstance(chainB[-2], self.cls.NiCollisionObject))
    assert(isinstance(chainB[-3], self.cls.NiNode))
    # return the relative transform
    return (chainA[-3].getTransform(relative_to = parent)
            * chainB[-3].getTransform(relative_to = parent).getInverse())

