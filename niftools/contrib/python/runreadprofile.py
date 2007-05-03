# --------------------------------------------------------------------------
# runreadprofile.py
# reads all nif & kf files from a specified folder, and dumps profile info
# --------------------------------------------------------------------------

from __future__ import generators
import os, stat, types, re, sys
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

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
    print """Usage:  python runreadprofile.py -p <path>
Example:  python runreadtest.py -p /home/user/nifs

Switches:
-? [Help]
   Displays This Information

-p [Search Path]
   Specifies the directory to search for files matching the input file name.
   If no path is specified, the present directory is searched.  Don't specify
   a path in the in file or the read will fail.
   Example:  -p 'C:\\Program Files\\'
"""

#default values
block_match = False
exclusive_mode = False
use_start_dir = False
blk_match_str = ""
start_dir = os.getcwd()

#examine command line arguments
help_flag = False
prev = ""
for i in sys.argv:
    # Evaluate flags that have an argument
    # If prev is a flag, record the value
    if prev == "-p":
        # search path
        start_dir = i

    # Record previous value in lowercase
    prev = i.lower()

if help_flag == True or len(sys.argv) <= 1:
    #Help request intercepted
    PrintHelpInfo()
    exit

re_nif = re.compile(r'^.*\.(nif|kf|kfa|nifcache)$', re.IGNORECASE)

def test():
    for top, names in walktree(start_dir):
   	for name in names:
            if (re_nif.match(name)):
                fname = os.path.join(top, name)
                print "*** reading %s ***"%fname,
                f = open(fname, "rb")
                f = StringIO(f.read(-1)) # reads entire file in memory
                version, user_version = NifFormat.getVersion(f)
                if version >= 0:
                    try:
                        print "(version 0x%08X)"%version
                        blocks = NifFormat.read(version, user_version, f)
                    except:
                        HexDump(f)
                        raise
                elif version == -1:
                    print 'nif version not supported'
                else:
                    print 'not a nif file'
            
                f.close()

try:
    import cProfile
    profile = cProfile
except ImportError:
    import profile

profile.run("test()", "profile.txt")
    
# print slowest functions, sorted by time
# (including time spent in subfunctions)

import pstats

p = pstats.Stats("profile.txt")
p.strip_dirs()
p.sort_stats('cumulative')
p.print_stats()
