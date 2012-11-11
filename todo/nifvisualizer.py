#!/usr/bin/python

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, NIF File Format Library and Tools.
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

import sys, os.path

Args = sys.argv

if len( Args ) < 3:
    print """
    nifvisualizer: Visualizes arbitrary block types by scriptable visualizers.
    ---
    Syntax: python nifvisualizer.py <file_name> <block_name> [alt]
    ---
    Usage:  Specify the Nif file with the <file_name> argument.
            The visualizer will look for a file called "<block_name>.py" in the
            "lizers" folder. If [alt] was specified, the visualizer
            "<block_name>_[alt].py" will be used.
    """
    sys.exit( 1 )

FileName = Args[1]
BlockName = Args[2]



sys.path.append( os.path.abspath( '../pymodules' ) )



from NifVis import vis_nif

vis_nif.LoadNif( FileName )



DrawBlocks = None

if vis_nif.TypeRegistry.has_key( BlockName ):
    DrawBlocks = vis_nif.TypeRegistry[BlockName]

if not DrawBlocks:
    print "Blocktype '%s' was not found in file!" % BlockName
    sys.exit( 1 )



from NifVis import lizers

LizerName = BlockName
if len( Args ) > 3:
    LizerName += '_' + Args[3]

Lizer = getattr(lizers, LizerName)

if not Lizer:
    print "Blocktype '%s' has no visualizer!" % BlockName
    sys.exit( 1 )



from NifVis import vis_gl

Radius = 1
for b in DrawBlocks:
    r = Lizer.Radius( b )
    if r > Radius: Radius = r

vis_gl.Initialize( Radius )

#try:
#    glBindTexture( Lizer.Texture() )
#except:
#    pass



from NifVis import vis_run

vis_run.Initialize()



while vis_run.IsRunning:
    vis_gl.InitFrame()

    vis_gl.DrawAxes()

    for b in DrawBlocks:
        vis_gl.InitDraw()
        Lizer.Draw( b )
        vis_gl.FinalizeDraw()

    vis_run.EventHandler()

    vis_gl.FinalizeFrame()
