import sys, os

_EXTENSIONS = ['.nif']

Args = sys.argv

if len( Args ) < 3:
    print """
    NifTester: Run arbitrary tests on files by scriptable testers.
    ---
    Syntax: NifTester.py [<file> | <dir>] <tester>
    ---
    Usage:  Specify the Nif file with the first argument, or specify
            a folder name instead.
            NifTester will look for a file called "<tester>.py" in the
            "testers" folder and use it for testing.
    """
    sys.exit( 1 )

FileName = Args[1]
TesterName = Args[2]



sys.path.append( os.path.abspath( '../pymodules' ) )



FileAccess = 1
DirAccess = 2

AccessMode = 0
if os.path.isfile( FileName ):
    AccessMode = FileAccess
elif os.path.isdir( FileName ):
    AccessMode = DirAccess
if AccessMode == 0:
    print "Error: '%s' is not a file or directory." % FileName
    sys.exit( 1 )



import testers
    
Tester = testers.Get( TesterName )

if not Tester:
    print "Tester '%s' was not found!" % TesterName
    sys.exit( 1 )



from NifFormat.NifFormat import NifFormat



class NIFImportError( Exception ):
    def __init__( self, message ):
        self.message = message
    def __str__( self ):
        return repr( self.message )


def TestDir( dirname ):
    global _EXTENSIONS
    subdirs = []
    contents = os.listdir( dirname )
    for file in contents:
        if os.path.isdir( os.path.join( dirname, file ) ):
            subdirs.append( file )
            continue
        
        file_name, ext = os.path.splitext( file )
        if ext in _EXTENSIONS:
            TestFile( os.path.join( dirname, file ), False )
    
    for dir in subdirs:
        TestDir( os.path.join( dirname, dir ) )


def TestFile( filename, report ):
    try:
        f = open( filename, "rb" )
        Version, UserVersion = NifFormat.getVersion( f )
        if Version >= 0:
                root_blocks = NifFormat.read( Version, UserVersion, f, verbose = 0 )
                for block in root_blocks:
                    TestBlock( filename, block, Version, UserVersion )
        elif Version == -1:
            raise NIFImportError( "Unsupported NIF version." )
        else:
            raise NIFImportError( "Not a NIF file." )
    
    except Exception, e:
        if not report: return
        global FileName, AccessMode
        fname = filename
        if AccessMode == FileAccess:
            fname = os.path.basename( fname )
        else:
            fname = fname[len(FileName)+1:]
        print '%s: Error - %s' % ( fname, e.message )
        return


def TestBlock( filename, block, ver1, ver2 ):
    global Tester, FileName, AccessMode
    
    if Tester.isApplicable( block ):
        result = Tester.Run( block )
        if result:
            fname = filename
            if AccessMode == FileAccess:
                fname = os.path.basename( fname )
            else:
                fname = fname[len(FileName)+1:]
            
            blkdesc = block.__class__.__name__
            try:
                blkdesc = Tester.Result( block )
            except:
                try:
                    blkdesc = block.name
                except:
                    pass
            print "%s: %s" % ( fname, blkdesc )
    
    for child in block.getRefs():
        TestBlock( filename, child, ver1, ver2 )



print "-------------------------"

if AccessMode == FileAccess:
    print "Testing file %s..." % FileName
    TestFile( FileName, True )

elif AccessMode == DirAccess:
    print "Testing directory %s..." % FileName
    TestDir( FileName )

print "-------------------------"
print "Done."
