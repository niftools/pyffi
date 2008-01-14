"""Custom MtlChunk functions."""

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

def getNameShaderScript(self):
    """Extract name, shader, and script."""
    name = self.name
    shader_begin = name.find("(")
    shader_end = name.find(")")
    script_begin = name.find("/")
    if (script_begin != -1):
        if (name.count("/") != 1):
            # must have exactly one script
            raise ValueError("%s malformed, has multiple ""/"""%name)
        mtlscript = name[script_begin+1:]
    else:
        mtlscript = ""
    if (shader_begin != -1): # if a shader was specified
        mtl_end = shader_begin
        # must have exactly one shader
        if (name.count("(") != 1):
            # some names are buggy and have "((" instead of "("
            # like in jungle_camp_sleeping_barack
            # here we handle that case
            if name[shader_begin + 1] == "(" \
               and name[shader_begin + 1:].count("(") == 1:
                shader_begin += 1
            else:
                raise ValueError("%s malformed, has multiple ""("""%name)
        if (name.count(")") != 1):
            raise ValueError("%s malformed, has multiple "")"""%name)
        # shader name should non-empty
        if shader_begin > shader_end:
            raise ValueError("%s malformed, ""("" comes after "")"""%name)
        # script must be immediately followed by the material
        if (script_begin != -1) and (shader_end + 1 != script_begin):
            raise ValueError("%s malformed, shader not followed by script"%name)
        mtlname = name[:mtl_end]
        mtlshader = name[shader_begin+1:shader_end]
    else:
        if script_begin != -1:
            mtlname = name[:script_begin]
        else:
            mtlname = name[:]
        mtlshader = ""
    return mtlname, mtlshader, mtlscript
