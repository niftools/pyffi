"""
Usage:  python runreadtest.py -p [path] -v [verbosity]
Example:  python runreadtest.py -p /home/user/nifs -v 1

Switches:
-p [path]
   Specifies the directory to search for files. If this flag is not specified,
   then the present directory is searched.

-v [verbosity]
"""

# --------------------------------------------------------------------------
# runreadtest.py
# reads all nif & kf files from a specified folder, and dumps them to
# the screen; very useful for debugging and testing purposes
# --------------------------------------------------------------------------

import os, stat, types, re, sys

from NifFormat.NifFormat import NifFormat

#default values
start_dir = os.getcwd()
verbosity = 0

#examine command line arguments
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

    # Record previous value in lowercase
    prev = i.lower()

def raise_exception(e):
    raise e

for roots in NifFormat.walk(start_dir, verbose = verbosity): #, onerror = raise_exception):
    pass
