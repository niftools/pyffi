# --------------------------------------------------------------------------
# runreadwritetest.py
# reads all nif & kf files from a specified folder, and writes them back to
# the disk; very useful for debugging and testing purposes
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
    if prev == "-p":
        # search path
        start_dir = i
    elif prev == "-v":
        # verbosity
        verbosity = int(i)

    if i == "-?":
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
                    roots = NifFormat.read(version, user_version, f, verbose = verbosity)
                except KeyboardInterrupt:
                    raise
                except:
                    HexDump(f, numLines = 32)
                    raise
            elif version == -1:
                print 'nif version not supported'
            else:
                print 'not a nif file'
            
            f.close()
            f = open('test.nif', 'wb')
            print "*** writing test.nif ***"
            try:
                NifFormat.write(version, user_version, f, roots, verbose = verbosity)
            except KeyboardInterrupt:
                raise
            except:
                raise
            finally:
                f.close()

            # compare the two files
            f1 = open(fname, 'rb')
            f2 = open('test.nif', 'rb')
            try:
                s1 = f1.read(-1)
                s2 = f2.read(-1)
                if s1 != s2:
                    f1.seek(0)
                    f2.seek(0)
                    print "*** TEST ERROR ***"
                    print "*** read:"
                    print NifFormat.read(version, user_version, f1, verbose = 2)
                    print "*** written:"
                    print NifFormat.read(version, user_version, f2, verbose = 2)
                    raise ValueError('nif file ' + fname + ' not written back identically')
            finally:
                f1.close()
                f2.close()
