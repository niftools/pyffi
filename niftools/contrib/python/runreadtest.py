# --------------------------------------------------------------------------
# runreadtest.py
# reads all nif & kf files from a specified folder, and dumps them to
# the screen; very useful for debugging and testing purposes
# --------------------------------------------------------------------------

from __future__ import generators
import os, stat, types, re, sys


from NifFormat.NifFormat import NifFormat
from FileFormat.HexDump import HexDump

# the walktree function is from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/200131
def walktree(top = ".", depthfirst = True):
    """Walk the directory tree, starting from top. Credit to Noah Spurrier and Doug Fort."""
    names = os.listdir(top)
    if not depthfirst:
        yield top, names
    for name in names:
        try:
            st = os.lstat(os.path.join(top, name))
        except os.error:
            continue
        if stat.S_ISDIR(st.st_mode):
            for (newtop, children) in walktree (os.path.join(top, name), depthfirst):
                yield newtop, children
    if depthfirst:
        yield top, names

def PrintHelpInfo():
    print """Usage:  python checkxml.py -switch_1 value_1 -switch_2 value_2 ... switch_n value_n
Example:  python runreadtest.py -p /home/user/nifs

Switches:
-? [Help]
   Displays This Information

-p [Search Path]
   Specifies the directory to search for files matching the input file name.
   If no path is specified, the present directory is searched.  Don't specify
   a path in the in file or the read will fail.
   Example:  -p 'C:\\Program Files\\'

-b [Block Match]
   Output information only for files which contain the specified block
   type. Default behavior is to output information about all files
   read.
   Example: -b NiNode

-x [Exclusive Mode]
   Output only the blocks that match the block type specified with the
   -b switch.  Normally the whole file that contians the block is
   output.
   Example: -x

-v [Verbosity]
"""

#default values
block_match = False
exclusive_mode = False
use_start_dir = False
blk_match_str = ""
start_dir = os.getcwd()
verbosity = 0

#examine command line arguments
help_flag = False
prev = ""
for i in sys.argv:
    # Evaluate flags that have an argument
    # If prev is a flag, record the value
    if prev == "-i":
        # input flag
        in_file = i
    elif prev == "-p":
        # search path
        start_dir = i
    elif prev == "-b":
        # block match
        block_match = i
    elif prev == "-v":
        # verbosity
        verbosity = int(i)

    # Evaluate flags that don't have arguments
    if i == "-x":
        # exclusive mode
        exclusive_mode = True
    elif i == "-?":
        # help mode
        help_flag = True

    # Record previous value in lowercase
    prev = i.lower()

if help_flag == True or len(sys.argv) <= 1:
    #Help request intercepted
    PrintHelpInfo()
    exit

re_nif = re.compile(r'^.*\.(nif|kf|kfa|nifcache)$', re.IGNORECASE)
for top, names in walktree(start_dir):
    for name in names:
        if (re_nif.match(name)):
            fname = os.path.join(top, name)
            print "*** reading %s ***"%fname,
            f = open(fname, "rb")
            version, user_version = NifFormat.getVersion(f)
            if version >= 0:
                try:
                    print "(version 0x%08X)"%version
                    blocks = NifFormat.read(version, user_version, f, verbose = verbosity)
                except KeyboardInterrupt:
                    raise
                except:
                    HexDump(f, numLines = 32)
                    #raise
            elif version == -1:
                print 'nif version not supported'
            else:
                print 'not a nif file'
            
            f.close()

            #print blocks

            #for b in blocks:
            #    if b.block_type.value == "NiControllerSequence":
            #        print b
