#!/usr/bin/python

"""A script for dumping texture and material information from nifs."""

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

from PyFFI.Formats.NIF import NifFormat

def testBlock(block, **args):
    """Print texture information.

    @param block: The block whose texture information to print.
    @type block: L{NifFormat.NiObject}
    """
    # modify to your needs
    if isinstance(block, NifFormat.NiGeometry):
        print("  geometry [%s] %s"%(block.__class__.__name__, block.name))
        for tex in block.tree(block_type = NifFormat.NiTexturingProperty):
            print("    [%s] %s"%(tex.__class__.__name__, tex.name))
            for textype in ('Base', 'Dark', 'Detail', 'Gloss', 'Glow',
                            'BumpMap', 'Decal0', 'Decal1', 'Decal2', 'Decal3'):
                if getattr(tex, 'has%sTexture' % textype):
                    texdesc = getattr(tex,
                                      '%s%sTexture'
                                      % (textype[0].lower(), textype[1:]))
                    if texdesc.source:
                        if texdesc.source.useExternal:
                            filename = texdesc.source.fileName
                        else:
                            filename = '(pixel data packed in file)'
                    else:
                        filename = '(no texture file)'
                    print("      [%s] %s" % (textype, filename))
            print("      apply mode %i" % tex.applyMode)
        for mtl in block.tree(block_type = NifFormat.NiMaterialProperty):
            print("    [%s] %s" % (mtl.__class__.__name__, mtl.name))
            for coltype in ['ambient', 'diffuse', 'specular', 'emissive']:
                col = getattr(mtl, '%sColor' % coltype)
                print('      %-10s %4.2f %4.2f %4.2f'
                      % (coltype, col.r, col.g, col.b))
            print('      glossiness %f' % mtl.glossiness)
            print('      alpha      %f' % mtl.alpha)

