"""Custom functions for NiBSplineCompTransformInterpolator."""

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

# TODO implement actual bspline sampling

def _getCompKeys(self, offset, element_size, bias, multiplier):
    """Helper function to get iterator to various keys. Internal use only."""
    # are there keys?
    if offset == 32767:
        return
    # yield all keys
    for key in self.splineData.getCompData(offset,
                                           self.basisData.numControlPoints,
                                           element_size,
                                           bias, multiplier):
        yield key

def getTranslations(self):
    """Return an iterator over all translation keys."""
    return self._getCompKeys(self.translationOffset, 3,
                             self.translationBias, self.translationMultiplier)

def getRotations(self):
    """Return an iterator over all rotation keys."""
    return self._getCompKeys(self.rotationOffset, 4,
                             self.rotationBias, self.rotationMultiplier)

def getScales(self):
    """Return an iterator over all scale keys."""    
    for key in self._getCompKeys(self.scaleOffset, 1,
                                 self.scaleBias, self.scaleMultiplier):
        yield key[0]
