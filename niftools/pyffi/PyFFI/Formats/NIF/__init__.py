"""This module sets up the NifFormat class, implementing the NIF file format.

Examples
========

Read a NIF file
---------------

>>> stream = open('tests/nif/test.nif', 'rb')
>>> data = NifFormat.Data()
>>> # inspect is optional; it will not read the actual blocks
>>> data.inspect(stream)
>>> hex(data.version)
'0x14010003'
>>> data.user_version
0
>>> print [blocktype for blocktype in data.header.blockTypes]
['NiNode', 'NiTriShape', 'NiTriShapeData']
>>> data.roots # blocks have not been read yet, so this is an empty list
[]
>>> data.read(stream)
>>> for root in data.roots:
...     for block in root.tree():
...         if isinstance(block, NifFormat.NiNode):
...             print block.name
test

The old deprecated method (for doctesting purposes only; in new code, use the
above method with L{NifFormat.Data}!):

>>> # get version and user version, and read nif file
>>> f = open('tests/nif/test.nif', 'rb')
>>> version, user_version = NifFormat.getVersion(f)
>>> if version == -1:
...     raise RuntimeError('nif version not supported')
... elif version == -2:
...     raise RuntimeError('not a nif file')
>>> roots = NifFormat.read(f, version = version, user_version = user_version)
>>> # print all NiNode names
>>> for root in roots:
...     for block in root.tree():
...         if isinstance(block, NifFormat.NiNode):
...             print block.name
test

Parse all NIF files in a directory tree
---------------------------------------

>>> for stream, data in NifFormat.walkData('tests/nif'):
...     try:
...         # the replace call makes the doctest also pass on windows
...         print("reading %s" % stream.name.replace("\\\\", "/"))
...         data.read(stream)
...     except StandardError:
...         print("Warning: read failed due corrupt file, corrupt format description, or bug.")
reading tests/nif/invalid.nif
Warning: read failed due corrupt file, corrupt format description, or bug.
reading tests/nif/test.nif
reading tests/nif/test_dump_tex.nif
reading tests/nif/test_fix_clampmaterialalpha.nif
reading tests/nif/test_fix_detachhavoktristripsdata.nif
reading tests/nif/test_fix_ffvt3rskinpartition.nif
reading tests/nif/test_fix_tangentspace.nif
reading tests/nif/test_fix_texturepath.nif
reading tests/nif/test_opt_dupgeomdata.nif
reading tests/nif/test_opt_dupverts.nif
reading tests/nif/test_opt_emptyproperties.nif
reading tests/nif/test_opt_mergeduplicates.nif

Create a NIF model from scratch and write to file
-------------------------------------------------

>>> root = NifFormat.NiNode()
>>> root.name = 'Scene Root'
>>> blk = NifFormat.NiNode()
>>> root.addChild(blk)
>>> blk.name = 'new block'
>>> blk.scale = 2.4
>>> blk.translation.x = 3.9
>>> blk.rotation.m11 = 1.0
>>> blk.rotation.m22 = 1.0
>>> blk.rotation.m33 = 1.0
>>> ctrl = NifFormat.NiVisController()
>>> ctrl.flags = 0x000c
>>> ctrl.target = blk
>>> blk.addController(ctrl)
>>> blk.addController(NifFormat.NiAlphaController())
>>> strips = NifFormat.NiTriStrips()
>>> root.addChild(strips, front = True)
>>> strips.name = "hello world"
>>> strips.rotation.m11 = 1.0
>>> strips.rotation.m22 = 1.0
>>> strips.rotation.m33 = 1.0
>>> data = NifFormat.NiTriStripsData()
>>> strips.data = data
>>> data.numVertices = 5
>>> data.hasVertices = True
>>> data.vertices.updateSize()
>>> for i, v in enumerate(data.vertices):
...     v.x = 1.0+i/10.0
...     v.y = 0.2+1.0/(i+1)
...     v.z = 0.03
>>> data.updateCenterRadius()
>>> data.numStrips = 2
>>> data.stripLengths.updateSize()
>>> data.stripLengths[0] = 3
>>> data.stripLengths[1] = 4
>>> data.hasPoints = True
>>> data.points.updateSize()
>>> data.points[0][0] = 0
>>> data.points[0][1] = 1
>>> data.points[0][2] = 2
>>> data.points[1][0] = 1
>>> data.points[1][1] = 2
>>> data.points[1][2] = 3
>>> data.points[1][3] = 4
>>> data.numUvSets = 1
>>> data.hasUv = True
>>> data.uvSets.updateSize()
>>> for i, v in enumerate(data.uvSets[0]):
...     v.u = 1.0-i/10.0
...     v.v = 1.0/(i+1)
>>> data.hasNormals = True
>>> data.normals.updateSize()
>>> for i, v in enumerate(data.normals):
...     v.x = 0.0
...     v.y = 0.0
...     v.z = 1.0
>>> strips.updateTangentSpace()
>>> from tempfile import TemporaryFile
>>> f = TemporaryFile()
>>> NifFormat.write(f, version = 0x14010003, user_version = 10, roots = [root])

Get list of versions and games
------------------------------

>>> for vnum in sorted(NifFormat.versions.values()): print '0x%08X'%vnum
0x02030000
0x03000000
0x03000300
0x03010000
0x0303000D
0x04000000
0x04000002
0x0401000C
0x04020002
0x04020100
0x04020200
0x0A000100
0x0A000102
0x0A000103
0x0A010000
0x0A010065
0x0A01006A
0x0A020000
0x14000004
0x14000005
0x14010003
0x14020007
0x14020008
0x14030001
0x14030002
0x14030003
0x14030006
0x14030009
>>> for game, versions in sorted(NifFormat.games.items(), key=lambda x: x[0]):
...     print game,
...     for vnum in versions:
...         print '0x%08X'%vnum,
...     print
? 0x0A000103
Atlantica 0x14020008
Axis and Allies 0x0A010000
Civilization IV 0x04020002 0x04020100 0x04020200 0x0A000100 0x0A010000 \
0x0A020000 0x14000004
Culpa Innata 0x04020200
Dark Age of Camelot 0x02030000 0x03000300 0x03010000 0x0401000C 0x04020100 0x04020200 \
0x0A010000
Emerge 0x14020007 0x14020008 0x14030001 0x14030002 0x14030003 0x14030006
Empire Earth II 0x04020200
Empire Earth III 0x14020007 0x14020008
Entropia Universe 0x0A010000
Fallout 3 0x14020007
Freedom Force 0x04000000 0x04000002
Freedom Force vs. the 3rd Reich 0x0A010000
Kohan 2 0x0A010000
Loki 0x0A020000
Megami Tensei: Imagine 0x14010003
Morrowind 0x04000002
Oblivion 0x0303000D 0x0A000102 0x0A010065 0x0A01006A 0x0A020000 0x14000004 \
0x14000005
Prison Tycoon 0x0A020000
Pro Cycling Manager 0x0A020000
Red Ocean 0x0A020000
Sid Meier's Railroads 0x14000004
Star Trek: Bridge Commander 0x03000000 0x03010000
The Guild 2 0x0A010000
Warhammer 0x14030009
Wildlife Park 2 0x0A010000 0x0A020000
Zoo Tycoon 2 0x0A000100
"""

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

# main nif format class

from PyFFI.Formats.NIF._NifFormat import NifFormat

# class customizers

import PyFFI.Formats.NIF._Header
import PyFFI.Formats.NIF._Matrix33
import PyFFI.Formats.NIF._Vector3
import PyFFI.Formats.NIF._Vector4

