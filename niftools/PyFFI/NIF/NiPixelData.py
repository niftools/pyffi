"""Custom functions for NiPixelData."""

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

from PyFFI.DDS import DdsFormat

def saveAsDDS(self, stream):
    """Save image as DDS file."""
    # set up header and pixel data
    header = DdsFormat.Header()
    data = DdsFormat.PixelData()

    # create header, depending on the format
    if self.pixelFormat in (self.cls.PixelFormat.PX_FMT_RGB8,
                            self.cls.PixelFormat.PX_FMT_RGBA8):
        # uncompressed RGB(A)
        header.flags.caps = 1
        header.flags.height = 1
        header.flags.width = 1
        header.flags.pixelFormat = 1
        header.flags.mipmapCount = 1
        header.flags.linearSize = 1
        header.height = self.mipmaps[0].height
        header.width = self.mipmaps[0].width
        header.linearSize = len(self.pixelData)
        header.mipmapCount = len(self.mipmaps)
        header.pixelFormat.flags.rgb = 1
        header.pixelFormat.bitCount = self.bitsPerPixel
        header.pixelFormat.rMask = self.redMask
        header.pixelFormat.gMask = self.greenMask
        header.pixelFormat.bMask = self.blueMask
        header.pixelFormat.aMask = self.alphaMask
        header.caps1.complex = 1
        header.caps1.texture = 1
        header.caps1.mipmap = 1
        data.setValue(self.pixelData)
    else:
        raise ValueError(
            "cannot save pixel format %i as DDS" % self.pixelFormat)

    DdsFormat.write(stream, version = 9, header = header, pixeldata = data)
