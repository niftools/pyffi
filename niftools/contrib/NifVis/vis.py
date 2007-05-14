import sys, os

Args = sys.argv

if len( Args ) < 3:
    print """
    NifVis: Visualizes arbitrary block types by scriptable visualizers.
    ---
    Syntax: vis.py <file_name> <block_name> [alt]
    ---
    Usage:  Specify the Nif file with the <file_name> argument.
            NifVis will look for a file called "<block_name>.py" in the
            "lizers" folder. If [alt] was specified, the visualizer
            "<block_name>_[alt].py" will be used.
    """
    sys.exit( 1 )

FileName = Args[1]
BlockName = Args[2]



sys.path.append( os.path.abspath( 'pymodules' ) )



if not os.path.exists('nif.xml'):
    print 'Please copy the nif.xml to use into the NifVis folder.'
    sys.exit( 1 )

os.putenv( 'NIFXMLPATH', os.path.dirname( __file__ ) )

import vis_nif

vis_nif.LoadNif( FileName )



DrawBlocks = None

if vis_nif.TypeRegistry.has_key( BlockName ):
    DrawBlocks = vis_nif.TypeRegistry[BlockName]
    
if not DrawBlocks:
    print "Blocktype '%s' was not found in file!" % BlockName
    sys.exit( 1 )



import lizers

LizerName = BlockName
if len( Args ) > 3:
    LizerName += '_' + Args[3]
    
Lizer = lizers.Get( LizerName )

if not Lizer:
    print "Blocktype '%s' has no visualizer!" % BlockName
    sys.exit( 1 )



import vis_gl

Radius = 1
for b in DrawBlocks:
    r = Lizer.Radius( b )
    if r > Radius: Radius = r

vis_gl.Initialize( Radius )

#try:
#    glBindTexture( Lizer.Texture() )
#except:
#    pass



import vis_run

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
