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

_NifMopp = WinDLL(os.path.join(os.path.dirname(__file__), "NifMopp.dll"))

def getMoppScaleOriginCode(vertices, triangles):
    """Generate mopp code for given geometry.

    For example, creating a mopp for the standard cube:

    >>> scale, orig, moppcode = getMoppScaleOriginCode(
    ...     [(1, 1, 1), (0, 0, 0), (0, 0, 1), (0, 1, 0),
    ...      (1, 0, 1), (0, 1, 1), (1, 1, 0), (1, 0, 0)],
    ...     [(0, 4, 6), (1, 6, 7), (2, 1, 4), (3, 1, 2),
    ...      (0, 2, 4), (4, 1, 7), (6, 4, 7), (3, 0, 6),
    ...      (0, 3, 5), (3, 2, 5), (2, 0, 5), (1, 3, 6)])
    >>> scale
    6.2187392503428082e-315
    >>> orig
    (-5.3776448224770004e-019, 1.5595011253197302e-314, 0.0)
    >>> moppcode
    [40, 0, 255, 39, 0, 255, 38, 0, 255, 22, 129, 126, 9, 38, 0, 3, 16, 3, 0, 1, 58, 56, 39, 0, 3, 16, 255, 0, 1, 49, 53]

    @param vertices: List of vertices.
    @type vertices: list of tuples of floats
    @param triangles: List of triangles (indices referring back to vertex list).
    @type triangles: list of tuples of ints
    @return: The mopp scale as a float, the origin as a tuple of floats, and
        the mopp code as a list of ints.
    """
    nverts = c_int(len(vertices))
    ntris = c_int(len(triangles))
    pverts = (c_double * (3 * len(vertices)))(*chain(*vertices))
    ptris = (c_short * (3 * len(triangles)))(*chain(*triangles))
    moppcodelen = _NifMopp.GenerateMoppCode(nverts, pverts, ntris, ptris)
    if moppcodelen == -1:
        raise RuntimeError("mopp generator failed")
    pmoppcode = create_string_buffer(moppcodelen)
    result = _NifMopp.RetrieveMoppCode(c_int(moppcodelen), pmoppcode)
    if result != moppcodelen:
        raise RuntimeError("retrieving mopp code failed")
    # convert c byte array to list of ints
    moppcode = list(ord(char) for char in pmoppcode)

    scale = c_double()
    if not _NifMopp.RetrieveMoppScale(byref(scale)):
        raise RuntimeError("retrieving mopp scale failed")
    # convert c_double to Python float
    scale = scale.value

    porigin = (c_double * 3)()
    if not _NifMopp.RetrieveMoppOrigin(porigin):
        raise RuntimeError("retreiving mopp origin failed")
    origin = tuple(value for value in porigin)
    #_NifMopp.RetrieveOrigin
    return scale, origin, moppcode
    

if __name__ == "__main__":
    import doctest
    doctest.testmod()
