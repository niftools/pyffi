"""Wrapper for NifMopp.dll"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
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
#    * Neither the name of the Python File Format Interface
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

from ctypes import *
from itertools import chain
import os.path

try:
    _NifMopp = WinDLL(os.path.join(os.path.dirname(__file__), "NifMopp.dll"))
except NameError:
    # on linux WinDLL will raise a NameError
    _NifMopp = None

def getMoppScaleOriginCode(vertices, triangles):
    """Generate mopp code for given geometry. Raises RuntimeError if something
    goes wrong (e.g. if mopp generator fails, or if NifMopp.dll cannot be
    loaded on the current platform).

    For example, creating a mopp for the standard cube:

    >>> scale, orig, moppcode = getMoppScaleOriginCode(
    ...     [(1, 1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0),
    ...      (1, 0, 1), (0, 1, 1), (1, 1, 0), (1, 0, 0)],
    ...     [(0, 4, 6), (1, 6, 7), (2, 1, 4), (3, 1, 2),
    ...      (0, 2, 4), (4, 1, 7), (6, 4, 7), (3, 0, 6),
    ...      (0, 3, 5), (3, 2, 5), (2, 0, 5), (1, 3, 6)])
    >>> scale
    16319749.0
    >>> ["%6.3f" % value for value in orig]
    ['-0.010', '-0.010', '-0.010']
    >>> moppcode
    [40, 0, 255, 39, 0, 255, 38, 0, 255, 19, 129, 125, 41, 22, 130, 125, 12, 24, 130, 125, 4, 38, 0, 5, 51, 39, 0, 5, 50, 24, 130, 125, 4, 40, 0, 5, 59, 16, 255, 249, 12, 20, 130, 125, 4, 39, 0, 5, 53, 40, 0, 5, 49, 54, 22, 130, 125, 25, 24, 130, 125, 17, 17, 255, 249, 12, 21, 129, 125, 4, 38, 0, 5, 57, 40, 249, 255, 58, 56, 40, 249, 255, 52, 24, 130, 125, 4, 39, 249, 255, 55, 38, 249, 255, 48]

    @param vertices: List of vertices.
    @type vertices: list of tuples of floats
    @param triangles: List of triangles (indices referring back to vertex list).
    @type triangles: list of tuples of ints
    @return: The mopp scale as a float, the origin as a tuple of floats, and
        the mopp code as a list of ints.
    """
    if _NifMopp is None:
        raise RuntimeError("havok mopp generator cannot run on this platform")
    nverts = c_int(len(vertices))
    ntris = c_int(len(triangles))
    pverts = (c_float * (3 * len(vertices)))(*chain(*vertices))
    ptris = (c_short * (3 * len(triangles)))(*chain(*triangles))
    moppcodelen = _NifMopp.GenerateMoppCode(nverts, pverts, ntris, ptris)
    if moppcodelen == -1:
        raise RuntimeError("havok mopp generator failed")
    pmoppcode = create_string_buffer(moppcodelen)
    result = _NifMopp.RetrieveMoppCode(c_int(moppcodelen), pmoppcode)
    if result != moppcodelen:
        raise RuntimeError("retrieving havok mopp code failed")
    # convert c byte array to list of ints
    moppcode = list(ord(char) for char in pmoppcode)

    scale = c_float()
    if not _NifMopp.RetrieveMoppScale(byref(scale)):
        raise RuntimeError("retrieving havok mopp scale failed")
    # convert c_double to Python float
    scale = scale.value

    porigin = (c_float * 3)()
    if not _NifMopp.RetrieveMoppOrigin(porigin):
        raise RuntimeError("retreiving havok mopp origin failed")
    origin = tuple(value for value in porigin)
    #_NifMopp.RetrieveOrigin
    return scale, origin, moppcode
    

if __name__ == "__main__":
    import doctest
    doctest.testmod()

