"""The PyFFI.Spells module bundles scripts for running hacking, surgery, and
validation spells. It is originally based on wz's NifTester module, although not
much of the original code that is left in this module.

These three functions in the spell script are called:

 - testRoot(block): will be called on every root block in the file
 - testBlock(block): will be called on every block in the file
 - testFile(stream, version, user_version, ...): will be called on every file

Not all of these three functions need to be present.
"""

# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------

import sys
import gc
from optparse import OptionParser

def testFileOverwrite(format, *walkresult, **kwargs):
    """Useful as testFile which simply writes back the file
    but restores the file if the write fails.

    @param format: The format class, e.g. L{PyFFI.Formats.CGF.CgfFormat}.
    @type format: subclass of L{PyFFI.XmlFileFormat}
    @param walkresult: Tuple with result from walkFile.
    @type walkresult: tuple
    """
    # first argument is always the stream, by convention
    stream = walkresult[0]
    stream.seek(0)
    backup = stream.read(-1)
    stream.seek(0)
    if kwargs.get('verbose'):
        print "  writing %s..."%stream.name
    #print(walkresult) # DEBUG
    try:
        format.write(*walkresult)
    except: # not just StandardError, also CTRL-C
        print "  write failed!!! attempt to restore original file..."
        stream.seek(0)
        stream.write(backup)
        stream.truncate()
        raise
    stream.truncate()

def testPath(top, format = None, spellmodule = None, verbose = 0, **kwargs):
    """Walk over all files in a directory tree and cast a particular spell
    on every file.

    @param top: The directory or file to test.
    @type top: str
    @param format: The format class, such as L{PyFFI.NIF.NifFormat}.
    @type format: L{PyFFI.XmlFileFormat} subclass
    @param spellmodule: The actual spell module.
    @type spellmodule: module
    @param verbose: Level of verbosity.
    @type verbose: int
    @param kwargs: Extra keyword arguments that will be passed to the spell.
    @type kwargs: dict
    """
    if format is None:
        raise ValueError("you must specify a format argument")
    if spellmodule is None:
        raise ValueError("you must specify a spellmodule argument")

    raisereaderror = getattr(spellmodule, "__raisereaderror__", True)
    readonly = getattr(spellmodule, "__readonly__", True)
    mode = 'rb' if readonly else 'r+b'
    verbose = kwargs.get("verbose", 1)
    pause = kwargs.get("pause", False)
    testRoot = getattr(spellmodule, "testRoot", None)
    testBlock = getattr(spellmodule, "testBlock", None)
    testFile = getattr(spellmodule, "testFile", None)
    spellkwargs = dict(**kwargs)

    # warning
    if not readonly:
        print("""This script will modify the nif files, in particular if something goes wrong it
may destroy them. Make a backup of your nif files before running this script.
""")
        if not raw_input("Are you sure that you want to proceed? [n/y] ") in ["y", "Y"]:
            if pause:
                raw_input("Script aborted by user.")
            else:
                print("Script aborted by user.")
            return

    # remind, walkresult is stream, version, user_version, and anything
    # returned by format.read appended to it
    # these are exactly the arguments accepted by write, so it identifies
    # the file uniquely
    for walkresult in format.walkFile(
        top, raisereaderror = raisereaderror,
        verbose = min(1, verbose), mode = mode):

        # result from read
        readresult = walkresult[3:]

        # cast all spells
        if testRoot:
            for block in format.getRoots(*readresult):
                testRoot(block, **spellkwargs)
        if testBlock:
            for block in format.getBlocks(*readresult):
                testBlock(block, **spellkwargs)
        if testFile:
            testFile(*walkresult, **spellkwargs)

        # save file back to disk if not readonly
        if not readonly:
            testFileOverwrite(format, *walkresult, **spellkwargs)

        # force free memory (this helps when parsing many very large files)
        del readresult
        del walkresult
        gc.collect()

def examples_callback(option, opt, value, parser, *args, **kwargs):
    """Print examples of usage."""
    examples = kwargs.get('examples')
    print examples
    sys.exit(0)

def spells_callback(option, opt, value, parser, *args, **kwargs):
    """Print all spells."""
    # get spells module
    formatspellsmodule = kwargs.get('formatspellsmodule')

    # print all submodules of the spells module
    for spell in dir(formatspellsmodule):
        if spell[:2] == '__':
            continue
        print(spell)

    # quit
    sys.exit(0)

def toaster(ext = None, format = None, formatspellsmodule = None,
            examples = None):
    """Main function to be called for toasters.

    @param ext: Three letter abbreviation of this format, e.g. 'TGA'.
    @type ext: str
    @param format: Format class, e.g. L{PyFFI.Formats.TGA.TgaFormat}.
    @type format: subclass of L{PyFFI.XmlFileFormat}.
    @param formatspellsmodule: The module where all spells can be found, e.g.
        L{PyFFI.Spells.TGA}.
    @type formatspellsmodule: module
    @param examples: A string listing some examples of usage.
    @type examples: str
    """
    # parse options and positional arguments
    usage = "%prog [options] <spell> <file>|<folder>"
    description="""Look for a python script "PyFFI.Spells.%s.<spell>"
and apply the functions testRoot, testBlock, and testFile therein
on the file <file>, or on the files in <folder>.""" % ext

    parser = OptionParser(usage, version="%prog $Rev$", description=description)
    parser.add_option("-a", "--arg", dest="arg",
                      type="string",
                      metavar="ARG",
                      help="pass argument ARG to spell")
    parser.add_option("--examples",
                      action="callback", callback=examples_callback,
                      callback_kwargs={'examples': examples},
                      help="show examples of usage and exit")
    parser.add_option("-r", "--raise", dest="raisetesterror",
                      action="store_true",
                      help="raise exception on errors during the spell")
    parser.add_option("-v", "--verbose", dest="verbose",
                      type="int",
                      metavar="VERBOSE",
                      help="verbosity level: 0, 1, or 2 [default: %default]")
    parser.add_option("-p", "--pause", dest="pause",
                      action="store_true",
                      help="pause when done")
    parser.add_option("-x", "--exclude", dest="exclude",
                      action="append",
                      help="exclude given block type from the spell \
(you can exclude multiple block types by specifying this option multiple \
times)")
    parser.add_option("--spells",
                      action="callback", callback=spells_callback,
                      callback_kwargs={'formatspellsmodule':
                                       formatspellsmodule},
                      help="list all spells and exit")
    parser.set_defaults(raisetesterror = False, verbose = 1, pause = False,
                        exclude = [])
    (options, args) = parser.parse_args()

    if len(args) != 2:
        parser.error("incorrect number of arguments (two required)")

    # get spell and top folder/file
    spell_str = args[0]
    top = args[1]

    try:
        spellfullmodule = __import__("%s.%s" % (formatspellsmodule.__name__,
                                                spell_str))
        spellmodule = getattr(formatspellsmodule, spell_str)
    except ImportError:
        # either spell was not found, or had an error while importing
        parser.error("spell '%s' not found" % spell_str)

    # run tester
    testPath(
        top, format = format, spellmodule = spellmodule,
        **parser.values)

    if options.pause:
        raw_input("Finished.")
