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

from cStringIO import StringIO
import gc
import optparse
import os
import os.path
import subprocess
import tempfile
from types import NoneType, ModuleType

import PyFFI # for PyFFI.__version__
import PyFFI.Spells.applypatch
import PyFFI.Utils.BSDiff

class Spell(object):
    """Spell base class. A spell takes a data file and then does something
    useful with it.

    @cvar READONLY: Whether the spell is read only or not.
    @type READONLY: C{bool}
    @ivar toaster: The toaster this spell is called from.
    @type toaster: L{Toaster}
    @ivar data: The data this spell acts on.
    @type data: L{PyFFI.ObjectModels.Data.Data}
    @ivar stream: The current file being processed.
    @type stream: C{file}
    """

    # spells are readonly by default
    READONLY = True

    def __init__(self, toaster, data, stream):
        """Initialize the spell data.

        @param toaster: The toaster this spell is called from.
        @type toaster: L{Toaster}
        @param data: The file data.
        @type data: L{PyFFI.ObjectModels.Data.Data}
        @param stream: The file stream.
        @type stream: C{file}
        """
        self.toaster = toaster
        self.data = data
        self.stream = stream

    def inspectdata(self):
        """This is called after L{PyFFI.ObjectModels.Data.Data.inspect} has
        been called, and before L{PyFFI.ObjectModels.Data.Data.read} is
        called.

        @return: C{True} if the file must be processed, C{False} otherwise.
        @rtype: C{bool}
        """
        # check if version applies
        # for nif: check if spell block type is found
        return True

    def inspectbranch(self, branch):
        """Check if spell should be cast on this branch or not, based on
        exclude and include options passed on the command line. You should
        not need to override this function: if you need additional checks on
        whether a branch must be parsed or not, override the L{spellentry}
        method.

        @param branch: The branch to check.
        @type branch: L{PyFFI.ObjectModels.Tree.GlobalTreeBranch}

        @return: C{True} if the branch must be processed, C{False} otherwise.
        @rtype: C{bool}
        """
        # always cast spell on the root data element
        if isinstance(branch, PyFFI.ObjectModels.Data.Data):
            return True
        # not a root, so check include and exclude options
        include = self.toaster.options.get("include", [])
        exclude = self.toaster.options.get("exclude", [])
        if not include:
            # everything is included
            return not(branch.__class__.__name__ in exclude)
        else:
            # if it is in exclude, exclude it
            if branch.__class__.__name__ in exclude:
                return False
            else:
                # else only include it if it is in the include list
                return (branch.__class__.__name__ in include)

    def recurse(self, branch=None):
        """Helper function which calls L{inspectbranch} on the branch,
        if successful then L{spellentry} on the branch, and if this is
        succesful it calls L{recurse} on the branch's children, and
        once all children are done, it calls L{spellexit}.

        You should not need to override this function, normally.

        @param branch: The branch to start the recursion from, or C{None}
            to recurse the whole tree.
        @type branch: L{PyFFI.ObjectModels.Tree.GlobalTreeBranch}
        """
        # when called without arguments, recurse over the whole tree
        if branch is None:
            if self.toaster.options.get("verbose"):
                print("=== " + self.__class__.__name__ + " ===")
            branch = self.data
        # if inspection is succesful
        if self.inspectbranch(branch):
            # cast the spell on the branch
            if self.spellentry(branch):
                # spell returned True so recurse to children
                # we use the abstract tree functions to parse the tree
                # these are format independent!
                for i in xrange(branch.getGlobalTreeNumChildren()):
                    child = branch.getGlobalTreeChild(i)
                    self.recurse(child)
                self.spellexit(branch)

    def spellentry(self, branch):
        """Cast the spell on the given branch. First called with branch equal to
        L{data}, then for all roots of data, then the children, grandchildren,
        and so on.
        The default implementation simply returns C{True}.

        Typically, you will override this function to perform an operation
        on a particular block type and/or to stop recursion at particular
        block types.

        @param branch: The branch to cast the spell on.
        @type branch: L{PyFFI.ObjectModels.Tree.GlobalTreeBranch}
        @return: C{True} if the children must be processed, C{False} otherwise.
        @rtype: C{bool}
        """
        return True

    def spellexit(self, branch):
        """Cast a spell on the given branch, after all its children,
        grandchildren, have been processed.

        Typically, you will override this function to perform a particular
        operation on a block type, but you rely on the fact that the children
        must have been processed first.

        @param branch: The branch to cast the spell on.
        @type branch: L{PyFFI.ObjectModels.Tree.GlobalTreeBranch}
        """
        pass

    @classmethod
    def toastentry(cls, toaster):
        """Called just before the toaster starts processing
        all files. If it returns C{False}, then the spell is not used.
        The default implementation simply returns C{True}.

        For example, if the spell only acts on a particular block type, but
        that block type is excluded, then you can use this function to flag
        that this spell can be skipped. You can also use this function to
        initialize statistics data to be aggregated from files, to
        initialize a log file, and so.

        @param toaster: The toaster this spell is called from.
        @type toaster: L{Toaster}
        @return: C{True} if the spell applies, C{False} otherwise.
        @rtype: C{bool}
        """
        return True

    @classmethod
    def toastexit(cls, toaster):
        """Called when the toaster has finished processing
        all files.

        @param toaster: The toaster this spell is called from.
        @type toaster: L{Toaster}
        """
        pass

class _MetaCompatSpell(type):
    """Metaclass for compatibility spell factory."""
    def __init__(cls, name, bases, dct):
        # make sure all test functions in the module exist (this makes it
        # easier on the wrapper implementation)
        if not hasattr(dct["SPELLMODULE"], "testFile"):
            dct["SPELLMODULE"].testFile = cls.stub
        if not hasattr(dct["SPELLMODULE"], "testRoot"):
            dct["SPELLMODULE"].testRoot = cls.stub
        if not hasattr(dct["SPELLMODULE"], "testBlock"):
            dct["SPELLMODULE"].testBlock = cls.stub
        # set readonly class variable
        dct["READONLY"] = getattr(dct["SPELLMODULE"], "__readonly__", True)
        # set documentation
        dct["__doc__"] = getattr(dct["SPELLMODULE"], "__doc__", "Undocumented.")
        # create the derived class
        super(_MetaCompatSpell, cls).__init__(name, bases, dct)

    @staticmethod
    def stub(*args, **kwargs):
        """Stub function."""
        pass

class _CompatSpell(Spell):
    """This is a spell class that can be instantiated from an
    old-style spell module. DO NOT USE FOR NEW SPELLS! Only for
    backwards compatibility.
    """
    SPELLMODULE = type("spellmod", (object,), {}) # stub
    __metaclass__ = _MetaCompatSpell

    def testFile(self, *args, **kwargs):
        self.SPELLMODULE.testFile(*args, **kwargs)

    def testBlock(self, *args, **kwargs):
        self.SPELLMODULE.testBlock(*args, **kwargs)

    def testRoot(self, *args, **kwargs):
        self.SPELLMODULE.testRoot(*args, **kwargs)

    def spellentry(self, branch):
        if isinstance(branch, PyFFI.ObjectModels.Data.Data):
            # the beginning; start with testing the roots
            for i in xrange(branch.getGlobalTreeNumChildren()):
                # the roots in the old system are the children of the data root
                root = branch.getGlobalTreeChild(i)
                self.testRoot(root, **self.toaster.options)
        else:
            # it is not the root data branch, 
            # now do the usual blocks
            self.testBlock(branch, **self.toaster.options)
        # enable further recursion in all cases
        return True

    def spellexit(self, branch):
        """Calls the testFile function."""
        if isinstance(branch, PyFFI.ObjectModels.Data.Data):
            # the root branch, so this is at the very end
            self.testFile(self.stream,
                          self.data.version, self.data.user_version,
                          self.data.roots,
                          **self.toaster.options)

class _MetaCompatToaster(type):
    """Metaclass for L{Toaster} which converts old-style module spells into
    new-style class spells.

    This is only for temporary use until all spells have been converted to
    the new class system.
    """

    def __init__(cls, name, bases, dct):
        # check the list of spells, and convert old-style modules to new-style
        # classes
        for i, spellclass in enumerate(dct["SPELLS"]):
            if isinstance(spellclass, ModuleType):
                dct["SPELLS"][i] = cls.CompatSpellFactory(spellclass)

    def CompatSpellFactory(cls, spellmod):
        """Create new-style spell class from old-style spell module.

        @param spellmod: The old-style spell module.
        @type spellmod: C{ModuleType}
        @return: The new-style spell class.
        @rtype: C{type(L{Spell})}
        """
        return type(spellmod.__name__.split(".")[-1], (_CompatSpell,),
                    {"SPELLMODULE": spellmod})


class Toaster:
    """Toaster base class. Toasters run spells on large quantities of files.
    They load each file and pass the data structure to any number of spells.

    @cvar FILEFORMAT: The file format class.
    @type FILEFORMAT: C{type(L{FileFormat})}
    @cvar SPELLS: List of all available spell classes.
    @type SPELLS: C{list} of C{type(L{Spell})}
    @cvar EXAMPLES: Description of example use.
    @type EXAMPLES: C{str}
    @ivar spellclasses: List of spell classes for the particular instance (must
        be a subset of L{SPELLS}).
    @type spellclasses: C{list} of C{type(L{Spell})}
    @ivar options: The options of the toaster.
    @type options: C{dict}
    """

    FILEFORMAT = NoneType # override when subclassing
    SPELLS = [] # override when subclassing
    EXAMPLES = "" # override when subclassing

    __metaclass__ = _MetaCompatToaster # for compatibility

    def __init__(self, spellclasses=None, options=None):
        """Initialize the toaster.

        @param spellclasses: List of spell classes.
        @type spellclasses: C{list} of C{type(L{Spell})}
        @param options: The options (as keyword arguments).
        @type options: C{dict}
        """
        self.spellclasses = spellclasses if spellclasses else []
        self.options = options if options else {}

    def cli(self):
        """Command line interface: initializes spell classes and options from
        the command line, and run the L{toast} method.
        """
        # parse options and positional arguments
        usage = "%prog [options] <spell1> <spell2> ... <file>|<folder>"
        description = """Apply the spells <spell1>, <spell2>, and so on,
on <file>, or recursively on <folder>."""
        errormessage_numargs = """incorrect number of arguments
(use the --help option for help)"""

        parser = optparse.OptionParser(
            usage,
            version="%%prog (PyFFI %s)" % PyFFI.__version__,
            description=description)
        parser.add_option("--help-spell", dest="helpspell",
                          action="store_true",
                          help="show help specific to the given spells")
        parser.add_option("--examples", dest="examples",
                          action="store_true",
                          help="show examples of usage and exit")
        parser.add_option("--spells", dest="spells",
                          action="store_true",
                          help="list all spells and exit")
        parser.add_option("-a", "--arg", dest="arg",
                          type="string",
                          metavar="ARG",
                          help="pass argument ARG to each spell")
        parser.add_option("-x", "--exclude", dest="exclude",
                          type="string",
                          action="append",
                          metavar="EXCLUDE",
                          help="exclude block type EXCLUDE from spell; \
exclude multiple block types by specifying this option more than once")
        parser.add_option("-i", "--include", dest="include",
                          type="string",
                          action="append",
                          metavar="INCLUDE",
                          help="include only block type INCLUDE in spell; \
if this option is not specified, then all block types are included except \
those specified under --exclude; \
include multiple block types by specifying this option more than once")
        parser.add_option("-r", "--raise", dest="raisetesterror",
                          action="store_true",
                          help="raise exception on errors during the spell; \
useful for debugging spells")
        parser.add_option("--noninteractive", dest="interactive",
                          action="store_false",
                          help="run a non-interactive session (overwrites \
files without warning)")
        parser.add_option("-v", "--verbose", dest="verbose",
                          type="int",
                          metavar="VERBOSE",
                          help="verbosity level: 0, 1, or 2 [default: %default]")
        parser.add_option("-p", "--pause", dest="pause",
                          action="store_true",
                          help="pause when done")
        parser.add_option("--dry-run", dest="dryrun",
                          action="store_true",
                          help="for spells that modify files, \
save the modification to a temporary file instead of writing it back to the \
original file; useful for debugging spells")
        parser.add_option("--prefix", dest="prefix",
                          type="string",
                          metavar="PREFIX",
                          help="for spells that modify files, \
prepend PREFIX to file name")
### no longer used
#        parser.add_option("--usetheforceluke", dest="raisereaderror",
#                          action="store_false",
#                          help="""pass exceptions while reading files;
#normally you do not need this, unless you are hacking the xml format
#description""")
        parser.add_option("--diff", dest="createpatch",
                          action="store_true",
                          help="""instead of writing back the file, write a \
binary patch""")
        parser.add_option("--patch", dest="applypatch",
                          action="store_true",
                          help="""apply all binary patches""")
        parser.add_option("--diff-cmd", dest="diffcmd",
                          type="string",
                          help="""use ARG as diff command; this command must \
accept precisely 3 arguments, oldfile, newfile, and patchfile.""")
        parser.add_option("--patch-cmd", dest="patchcmd",
                          type="string",
                          help="""use ARG as patch command; this command must \
accept precisely 3 arguments, oldfile, newfile, and patchfile.""")
        parser.set_defaults(raisetesterror=False, verbose=1, pause=False,
                            exclude=[], include=[], examples=False,
                            spells=False,
                            #raisereaderror=True, ### no longer used
                            interactive=True,
                            helpspell=False, dryrun=False, prefix="", arg="",
                            createpatch=False, applypatch=False, diffcmd="")
        (options, args) = parser.parse_args()

        # check errors
        if options.createpatch and options.applypatch:
            parser.error("options --diff and --patch are mutually exclusive")
        if options.diffcmd and not(options.createpatch):
            parser.error("option --diff-cmd can only be used with --diff")
        if options.patchcmd and not(options.applypatch):
            parser.error("option --patch-cmd can only be used with --patch")

        # check if we had examples and/or spells: quit
        if options.spells:
            for spellclass in self.SPELLS:
                print spellclass.__name__
            return
        if options.examples:
            print(self.EXAMPLES)
            return

        # spell name not specified when function was called
        if len(args) < 1:
            parser.error(errormessage_numargs)

        # check if we are applying patches
        if options.applypatch:
            if len(args) > 1:
                parser.error("when using --patch, do not specify a spell")
            # set spell class to applying patch
            self.spellclasses = [PyFFI.Spells.applypatch.Spell]
        else:
            # get spell names
            spellnames = args[:-1]
            # get spell classes
            self.spellclasses = [spellclass for spellclass in self.SPELLS
                                 if spellclass.__name__ in spellnames]

            if options.helpspell:
                # TODO: format the docstring
                for spellclass in self.spellclasses:
                    print(spellclass.__doc__)
                return

            # top not specified when function was called
            if len(args) < 2:
                parser.error(errormessage_numargs)

        # get top folder/file: last argument always is folder/file
        top = args[-1]

        # convert options to dictionary
        self.options = {}
        for optionname in dir(options):
            # skip default attributes of optparse.Values
            if not optionname in dir(optparse.Values):
                self.options[optionname] = getattr(options, optionname)

        self.toast(top)

        # signal the end
        if options.pause and options.interactive:
            raw_input("Finished.")
        else:
            print("Finished.")

    def readonly(self):
        """Returns whether the toaster has all readonly spells, or not.

        @return: C{True} if toaster is readonly, C{False} otherwise.
        @rtype: C{bool}
        """
        # the combined spells are readonly if and only if all spells are
        # readonly
        return all(spellclass.READONLY
                   for spellclass in self.spellclasses)

    def toast(self, top):
        """Walk over all files in a directory tree and cast spells
        on every file.

        @param top: The directory or file to toast.
        @type top: str
        """

        ### raisereaderror is ignored in this implementation!!!
        ### new-style toaster has it functionally equal to
        ### raisetesterror
        #raisereaderror = self.options.get("raisereaderror", True)
        verbose = self.options.get("verbose", 1)
        raisetesterror = self.options.get("raisetesterror", False)
        pause = self.options.get("pause", False)
        interactive = self.options.get("interactive", True)
        dryrun = self.options.get("dryrun", False)
        prefix = self.options.get("prefix", "")
        createpatch = self.options.get("createpatch", False)
        applypatch = self.options.get("applypatch", False)

        # warning
        if ((not self.readonly()) and (not dryrun)
            and (not prefix) and (not createpatch)
            and interactive):
            print("""\
This script will modify your files, in particular if something goes wrong it
may destroy them. Make a backup of your files before running this script.
""")
            if not raw_input(
                "Are you sure that you want to proceed? [n/y] ") in ("y", "Y"):
                if pause:
                    raw_input("Script aborted by user.")
                else:
                    print("Script aborted by user.")
                return

        # toast entry code
        self.spellclasses = [spellclass for spellclass in self.spellclasses
                             if spellclass.toastentry(self)]

        # if there are no spells left, quit early!
        if not self.spellclasses:
            if verbose:
                print("no spells apply! quiting early...")
            return

        # walk over all streams, and create a data instance for each of them
        # inspect the file but do not yet read in full
        for stream, data in self.FILEFORMAT.walkData(
            top, verbose=verbose, mode='rb' if self.readonly() else 'r+b'):

            try: 
                # inspect the file (reads only the header)
                data.inspect(stream)
 
                # create spell instances
                spells = [spellclass(self, data, stream)
                          for spellclass in self.spellclasses]
                
                # select those spells that must be cast
                spells = [spell for spell in spells
                          if spell.inspectdata()]

                # if there are any spells that apply
                if spells:
                    # read the full file
                    data.read(stream)
                    
                    # cast the spell on the data tree
                    for spell in spells:
                        spell.recurse()

                    # save file back to disk if not readonly
                    if not self.readonly():
                        if not dryrun:
                            if createpatch:
                                self._writepatch(stream, data)
                            elif prefix:
                                self._writeprefix(stream, data)
                            else:
                                self._writeover(stream, data)
                        else:
                            # write back to a temporary file
                            self._writetemp(stream, data)
            except StandardError:
                print("""\
*** TEST FAILED ON %-51s ***
*** If you were running a script that came with PyFFI, then            ***
*** please report this as a bug (include the file) on                  ***
*** http://sourceforge.net/tracker/?group_id=199269                    ***
""" % stream.name)
                # if raising test errors, reraise the exception
                if raisetesterror:
                    raise

            # force free memory (this helps when parsing many very large files)
            del spells
            del spell
            gc.collect()

        # toast exit code
        for spellclass in self.spellclasses:
            spellclass.toastexit(self)

def testFileTempwrite(format, *walkresult, **kwargs):
    """Useful as testFile which simply writes back the file
    to a temporary file and raises an exception if the write fails.

    @param format: The format class, e.g. L{PyFFI.Formats.CGF.CgfFormat}.
    @type format: subclass of L{PyFFI.XmlFileFormat}
    @param walkresult: Tuple with result from walkFile.
    @type walkresult: tuple
    @param kwargs: Extra keyword arguments.
    @type kwargs: dict
    """
    if kwargs.get('verbose'):
        print("  writing to temporary file...")
    stream = tempfile.TemporaryFile()
    try:
        # first argument is always the stream, by convention
        writeargs = (stream,) + walkresult[1:]
        try:
            format.write(*writeargs)
        except StandardError:
            print "  write failed!!!"
            raise
    finally:
        stream.close()

def testFilePrefixwrite(format, *walkresult, **kwargs):
    """Useful as testFile which simply writes back the file
    appending a prefix to the original file name.

    @param format: The format class, e.g. L{PyFFI.Formats.CGF.CgfFormat}.
    @type format: subclass of L{PyFFI.XmlFileFormat}
    @param walkresult: Tuple with result from walkFile.
    @type walkresult: tuple
    @param kwargs: Extra keyword arguments.
    @type kwargs: dict
    """
    # first argument is always the stream, by convention
    head, tail = os.path.split(walkresult[0].name)
    stream = open(os.path.join(head, kwargs["prefix"] + tail), "wb")
    try:
        if kwargs.get('verbose'):
            print("  writing %s..." % stream.name)
        #print(walkresult) # DEBUG
        writeargs = (stream,) + walkresult[1:]
        try:
            format.write(*writeargs)
        except StandardError:
            print "  write failed!!!"
            raise
    finally:
        stream.close()

def testFileOverwrite(format, *walkresult, **kwargs):
    """Useful as testFile which simply writes back the file
    but restores the file if the write fails.

    @param format: The format class, e.g. L{PyFFI.Formats.CGF.CgfFormat}.
    @type format: subclass of L{PyFFI.XmlFileFormat}
    @param walkresult: Tuple with result from walkFile.
    @type walkresult: tuple
    @param kwargs: Extra keyword arguments.
    @type kwargs: dict
    """
    # first argument is always the stream, by convention
    stream = walkresult[0]
    stream.seek(0)
    backup = stream.read(-1)
    stream.seek(0)
    if kwargs.get('verbose'):
        print("  writing %s..." % stream.name)
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

def testFileCreatePatch(format, *walkresult, **kwargs):
    """Useful as testFile which simply creates a binary patch for the
    updated file.

    @param format: The format class, e.g. L{PyFFI.Formats.CGF.CgfFormat}.
    @type format: subclass of L{PyFFI.XmlFileFormat}
    @param walkresult: Tuple with result from walkFile.
    @type walkresult: tuple
    @param kwargs: Extra keyword arguments.
    @type kwargs: dict
    """
    diffcmd = kwargs.get('diffcmd')
    # create a temporary file that won't get deleted when closed
    newfile = tempfile.NamedTemporaryFile()
    newfilename = newfile.name
    newfile.close()
    newfile = open(newfilename, "w+b")
    if kwargs.get('verbose'):
        print("  writing to temporary file...")
    #print(walkresult) # DEBUG
    try:
        format.write(newfile, *walkresult[1:])
    except: # not just StandardError, also CTRL-C
        print "  write failed!!!"
        raise
    # first argument is always the stream, by convention
    if not diffcmd:
        # use internal differ
        oldfile = walkresult[0]
        oldfile.seek(0)
        newfile.seek(0)
        patchfile = open(oldfile.name + ".patch", "wb")
        if kwargs.get('verbose'):
            print("  writing patch...")
        PyFFI.Utils.BSDiff.diff(oldfile, newfile, patchfile)
        patchfile.close()
        newfile.close()
    else:
        # use external diff command
        oldfile = walkresult[0]
        oldfilename = oldfile.name
        patchfilename = oldfilename + ".patch"
        # close all files before calling external command
        oldfile.close()
        newfile.close()
        if kwargs.get('verbose'):
            print("  calling %s..." % diffcmd)
        subprocess.call([diffcmd, oldfilename, newfilename, patchfilename])
    # delete temporary file
    os.remove(newfilename)

def isBlockAdmissible(block, exclude, include):
    """Check if a block should be tested or not, based on exclude and include
    options passed on the command line.

    @param block: The block to check.
    @type block: L{PyFFI.ObjectModels.XML.Struct.StructBase}
    @param exclude: List of blocks to exclude.
    @type exclude: list of str
    @param include: List of blocks to include.
    @type include: list of str
    """
    if not include:
        # everything is included
        return not(block.__class__.__name__ in exclude)
    else:
        # if it is in exclude, exclude it
        if block.__class__.__name__ in exclude:
            return False
        else:
            # else only include it if it is in the include list
            return (block.__class__.__name__ in include)

def testPath(top, format = None, spellmodule = None, **kwargs):
    """Walk over all files in a directory tree and cast a particular spell
    on every file.

    @param top: The directory or file to test.
    @type top: str
    @param format: The format class, such as L{PyFFI.NIF.NifFormat}.
    @type format: L{PyFFI.XmlFileFormat} subclass
    @param spellmodule: The actual spell module.
    @type spellmodule: module
    @param kwargs: Extra keyword arguments that will be passed to the spell,
        such as
          - verbose: Level of verbosity.
          - raisetesterror: Whether to raise errors that occur while casting
              the spell.
          - raisereaderror: Whether to raise errors that occur while reading
              the file.
          - exclude: List of blocks to exclude from the spell.
          - include: List of blocks to include in the spell.
          - prefix: File prefix when writing back.
          - createpatch: Whether to write back the result as a patch.
    @type kwargs: dict
    """
    if format is None:
        raise ValueError("you must specify a format argument")
    if spellmodule is None:
        raise ValueError("you must specify a spellmodule argument")

    readonly = getattr(spellmodule, "__readonly__", True)
    raisereaderror = kwargs.get("raisereaderror", True)
    verbose = kwargs.get("verbose", 1)
    raisetesterror = kwargs.get("raisetesterror", False)
    pause = kwargs.get("pause", False)
    interactive = kwargs.get("interactive", True)
    dryrun = kwargs.get("dryrun", False)
    prefix = kwargs.get("prefix", "")
    createpatch = kwargs.get("createpatch", False)
    applypatch = kwargs.get("applypatch", False)
    testRoot = getattr(spellmodule, "testRoot", None)
    testBlock = getattr(spellmodule, "testBlock", None)
    testFile = getattr(spellmodule, "testFile", None)

    # warning
    if ((not readonly) and (not dryrun) and not(prefix) and not(createpatch)
        and interactive):
        print("""\
This script will modify your files, in particular if something goes wrong it
may destroy them. Make a backup of your files before running this script.
""")
        if not raw_input(
            "Are you sure that you want to proceed? [n/y] ") in ("y", "Y"):
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
        top, raisereaderror=raisereaderror,
        verbose=verbose, mode='rb' if readonly else 'r+b'):

        # result from read
        readresult = walkresult[3:]

        try:
            # cast all spells
            if testRoot:
                for block in format.getRoots(*readresult):
                    if isBlockAdmissible(block = block,
                                         exclude = kwargs["exclude"],
                                         include = kwargs["include"]):
                        testRoot(block, **kwargs)
            if testBlock:
                for block in format.getBlocks(*readresult):
                    if isBlockAdmissible(block = block,
                                         exclude = kwargs["exclude"],
                                         include = kwargs["include"]):
                        testBlock(block, **kwargs)
            if testFile:
                testFile(*walkresult, **kwargs)

            # save file back to disk if not readonly
            if not readonly:
                if not dryrun:
                    if createpatch:
                        testFileCreatePatch(format, *walkresult, **kwargs)
                    elif prefix:
                        testFilePrefixwrite(format, *walkresult, **kwargs)
                    else:
                        testFileOverwrite(format, *walkresult, **kwargs)
                else:
                    # write back to a temporary file
                    testFileTempwrite(format, *walkresult, **kwargs)
        except StandardError:
            # walkresult[0] is the stream
            print("""\
*** TEST FAILED ON %-51s ***
*** If you were running a script that came with PyFFI, then            ***
*** please report this as a bug (include the file) on                  ***
*** http://sourceforge.net/tracker/?group_id=199269                    ***
""" % walkresult[0].name)
            # if raising test errors, reraise the exception
            if raisetesterror:
                raise

        # force free memory (this helps when parsing many very large files)
        del readresult
        del walkresult
        gc.collect()

def printexamples(examples):
    """Print examples of usage.

    @param examples: The string of examples. (Passed via kwargs.)
    @type examples: str
    """
    # print examples
    print(examples)

def printspells(formatspellsmodule):
    """Print all spells.

    @param formatspellsmodule: The spells module. (Passed via kwargs.)
    @type formatspellsmodule: module
    """
    # print all submodules of the spells module
    for spell in dir(formatspellsmodule):
        if spell[:2] == '__':
            continue
        # this is just a hack for the moment; the list of spells will be
        # stored elsewhere in a future version
        if spell in ("PyFFI", "NifSpell", "NifToaster"):
            continue
        print(spell)

def toaster(format=None, formatspellsmodule=None, examples=None):
    """Main function to be called for toasters. The spell is taken from
    the command line (such as with niftoaster, cgftoaster, etc.), along with
    any options.

    @param format: Format class, e.g. L{PyFFI.Formats.NIF.NifFormat}.
    @type format: subclass of L{PyFFI.XmlFileFormat}.
    @param formatspellsmodule: The module where all spells can be found, e.g.
        L{PyFFI.Spells.NIF}.
    @type formatspellsmodule: module
    @param examples: A string listing some examples of usage.
    @type examples: str
    """
    # parse options and positional arguments
    usage = "%prog [options] <spell> <file>|<folder>"
    description = """Apply a spell "%s.<spell>" on <file>, or recursively
on <folder>.""" % formatspellsmodule.__name__
    errormessage_numargs = """incorrect number of arguments
(use the --help option for help)"""

    parser = optparse.OptionParser(
        usage,
        version="%%prog (PyFFI %s)" % PyFFI.__version__,
        description=description)
    parser.add_option("--help-spell", dest="helpspell",
                      action="store_true",
                      help="show help specific to the given spell")
    parser.add_option("--examples", dest="examples",
                      action="store_true",
                      help="show examples of usage and exit")
    parser.add_option("--spells", dest="spells",
                      action="store_true",
                      help="list all spells and exit")
    parser.add_option("-a", "--arg", dest="arg",
                      type="string",
                      metavar="ARG",
                      help="pass argument ARG to spell")
    parser.add_option("-x", "--exclude", dest="exclude",
                      type="string",
                      action="append",
                      metavar="EXCLUDE",
                      help="exclude block type EXCLUDE from spell; \
exclude multiple block types by specifying this option more than once")
    parser.add_option("-i", "--include", dest="include",
                      type="string",
                      action="append",
                      metavar="INCLUDE",
                      help="include only block type INCLUDE in spell; \
if this option is not specified, then all block types are included except \
those specified under --exclude; \
include multiple block types by specifying this option more than once")
    parser.add_option("-r", "--raise", dest="raisetesterror",
                      action="store_true",
                      help="raise exception on errors during the spell; \
useful for debugging spells")
    parser.add_option("--noninteractive", dest="interactive",
                      action="store_false",
                      help="run a non-interactive session (overwrites files \
without warning)")
    parser.add_option("-v", "--verbose", dest="verbose",
                      type="int",
                      metavar="VERBOSE",
                      help="verbosity level: 0, 1, or 2 [default: %default]")
    parser.add_option("-p", "--pause", dest="pause",
                      action="store_true",
                      help="pause when done")
    parser.add_option("--dry-run", dest="dryrun",
                      action="store_true",
                      help="for spells that modify files, \
save the modification to a temporary file instead of writing it back to the \
original file; useful for debugging spells")
    parser.add_option("--prefix", dest="prefix",
                      type="string",
                      metavar="PREFIX",
                      help="for spells that modify files, \
prepend PREFIX to file name")
    parser.add_option("--usetheforceluke", dest="raisereaderror",
                      action="store_false",
                      help="""pass exceptions while reading files;
normally you do not need this, unless you are hacking the xml format
description""")
    parser.add_option("--diff", dest="createpatch",
                      action="store_true",
                      help="""instead of writing back the file, write a \
binary patch""")
    parser.add_option("--patch", dest="applypatch",
                      action="store_true",
                      help="""apply all binary patches""")
    parser.add_option("--diff-cmd", dest="diffcmd",
                      type="string",
                      help="""use ARG as diff command; this command must \
accept precisely 3 arguments, oldfile, newfile, and patchfile.""")
    parser.add_option("--patch-cmd", dest="patchcmd",
                      type="string",
                      help="""use ARG as patch command; this command must \
accept precisely 3 arguments, oldfile, newfile, and patchfile.""")
    parser.set_defaults(raisetesterror=False, verbose=1, pause=False,
                        exclude=[], include=[], examples=False, spells=False,
                        raisereaderror=True, interactive=True,
                        helpspell=False, dryrun=False, prefix="", arg="",
                        createpatch=False, applypatch=False, diffcmd="")
    (options, args) = parser.parse_args()

    # check errors
    if options.createpatch and options.applypatch:
        parser.error("options --diff and --patch are mutually exclusive")
    if options.diffcmd and not(options.createpatch):
        parser.error("option --diff-cmd can only be used with --diff")
    if options.patchcmd and not(options.applypatch):
        parser.error("option --patch-cmd can only be used with --patch")

    # check if we had examples and/or spells: quit
    if options.spells:
        printspells(formatspellsmodule)
        return
    if options.examples:
        printexamples(examples)
        return

    # spell name not specified when function was called
    if len(args) < 1:
        parser.error(errormessage_numargs)

    # check if we are applying patches
    if options.applypatch:
        if len(args) > 1:
            parser.error("when using --patch, do not specify a spell")
        # set spell module to applying patch
        spellmodule = PyFFI.Spells.applypatch
    else:
        # get spell name
        spellname = args[0]
        # get spell module
        try:
            spellmodule = getattr(formatspellsmodule, spellname)
        except AttributeError:
            # spell was not found
            parser.error("spell '%s' not found" % spellname)

        if options.helpspell:
            # TODO: format the docstring
            print(spellmodule.__doc__)
            return

        # top not specified when function was called
        if len(args) != 2:
            parser.error(errormessage_numargs)

    # get top folder/file: last argument always is folder/file
    top = args[-1]

    # convert options to dictionary
    optionsdict = {}
    for optionname in dir(options):
        # skip default attributes of optparse.Values
        if not optionname in dir(optparse.Values):
            optionsdict[optionname] = getattr(options, optionname)

    # run the spell
    testPath(top, format = format, spellmodule = spellmodule, **optionsdict)

    # signal the end
    if options.pause and options.interactive:
        raw_input("Finished.")
    else:
        print("Finished.")

