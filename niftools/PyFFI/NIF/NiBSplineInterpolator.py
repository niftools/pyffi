"""Custom functions for NiBSplineInterpolator."""

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

def getTimes(self):
    """Return an iterator over all key times."""
    for i in xrange(self.basisData.numControlPoints):
        yield self.startTime + (i * (self.stopTime - self.startTime)
                                / (self.basisData.numControlPoints - 1))

def _getFloatKeys(self, offset, element_size):
    """Helper function to get iterator to various keys. Internal use only."""
    # are there keys?
    if offset == 65535:
        return
    # yield all keys
    for key in self.splineData.getFloatData(offset,
                                            self.basisData.numControlPoints,
                                            element_size):
        yield key

def _getCompKeys(self, offset, element_size, bias, multiplier):
    """Helper function to get iterator to various keys. Internal use only."""
    # are there keys?
    if offset == 65535:
        return
    # yield all keys
    for key in self.splineData.getCompData(offset,
                                           self.basisData.numControlPoints,
                                           element_size,
                                           bias, multiplier):
        yield key

