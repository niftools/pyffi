import sys, os.path

Args = sys.argv

if len( Args ) < 3:
    print "Syntax: vis.py <file_name> <block_name> "
    sys.exit( 1 )

FileName = Args[1]
BlockName = Args[2]



sys.path.append( os.path.abspath( 'pymodules' ) )



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



import vis_run

vis_run.Initialize()



while vis_run.IsRunning: 
    vis_gl.InitFrame()
    
    vis_gl.DrawAxes()
    
    for b in DrawBlocks:
        Lizer.Draw( b )
    
    vis_run.EventHandler()
    
    vis_gl.FinalizeFrame()
