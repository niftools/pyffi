"""This module bundles scripts for running hacking, surgery, and
validation spells. It is originally based on wz's NifTester module, although
nothing of wz's original code is left in this module.

Derive your custom spells from the L{Spell} class, and include them in the
L{Toaster.SPELLS} variable of your toaster.

Spells can also run independently of toasters, and be applied on branches
directly. The recommended way of doing this is via the L{Spell.recurse}
function.
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
import sys # sys.stdout
import tempfile
from types import ModuleType # for _MetaCompatToaster

import PyFFI # for PyFFI.__version__
import PyFFI.Spells.applypatch
import PyFFI.Utils.BSDiff
import PyFFI.ObjectModels.FileFormat # PyFFI.ObjectModels.FileFormat.FileFormat

class Spell(object):
    """Spell base class. A spell takes a data file and then does something
    useful with it. The main entry point for spells is L{recurse}, so if you
    are writing new spells, start with reading the documentation with
    L{recurse}.

    @cvar READONLY: Whether the spell is read only or not.
    @type READONLY: C{bool}
    @cvar SPELLNAME: How to refer to the spell from the command line.
    @type SPELLNAME: C{str}
    @ivar toaster: The toaster this spell is called from.
    @type toaster: L{Toaster}
    @ivar data: The data this spell acts on.
    @type data: L{PyFFI.ObjectModels.FileFormat.FileFormat.Data}
    @ivar stream: The current file being processed.
    @type stream: C{file}
    """

    # spells are readonly by default
    READONLY = True
    SPELLNAME = None

    def __init__(self, toaster=None, data=None, stream=None):
        """Initialize the spell data.

        @kwarg data: The file data.
        @type data: L{PyFFI.ObjectModels.FileFormat.FileFormat.Data}
        @kwarg stream: The file stream.
        @type stream: C{file}
        @kwarg toaster: The toaster this spell is called from (optional).
        @type toaster: L{Toaster}
        """
        self.data = data
        self.stream = stream
        self.toaster = toaster if toaster else Toaster()

    def _datainspect(self):
        """This is called after C{L{data}.inspect} has
        been called, and before C{L{data}.read} is
        called.

        @return: C{True} if the file must be processed, C{False} otherwise.
        @rtype: C{bool}
        """
        # for the moment, this does nothing
        return True

    def datainspect(self):
        """This is called after C{L{data}.inspect} has
        been called, and before C{L{data}.read} is
        called. Override this function for customization.

        @return: C{True} if the file must be processed, C{False} otherwise.
        @rtype: C{bool}
        """
        # for nif: check if version applies, or
        # check if spell block type is found
        return True

    def _branchinspect(self, branch):
        """Check if spell should be cast on this branch or not, based on
        exclude and include options passed on the command line. You should
        not need to override this function: if you need additional checks on
        whether a branch must be parsed or not, override the L{branchinspect}
        method.

        @param branch: The branch to check.
        @type branch: L{PyFFI.ObjectModels.Tree.GlobalTree}
        @return: C{True} if the branch must be processed, C{False} otherwise.
        @rtype: C{bool}
        """
        # fall back on the toaster implementation
        return self.toaster.isadmissiblebranchtype(branch.__class__)

    def branchinspect(self, branch):
        """Like L{_branchinspect}, but for customization: can be overridden to
        perform an extra inspection (the default implementation always
        returns C{True}).

        @param branch: The branch to check.
        @type branch: L{PyFFI.ObjectModels.Tree.GlobalTree}
        @return: C{True} if the branch must be processed, C{False} otherwise.
        @rtype: C{bool}
        """
        return True

    def recurse(self, branch=None):
        """Helper function which calls L{_branchinspect} and L{branchinspect}
        on the branch,
        if both successful then L{branchentry} on the branch, and if this is
        succesful it calls L{recurse} on the branch's children, and
        once all children are done, it calls L{branchexit}.

        Note that L{_branchinspect} and L{branchinspect} are not called upon
        first entry of this function, that is, when called with L{data} as
        branch argument. Use L{datainspect} to stop recursion into this branch.

        Do not override this function.

        @param branch: The branch to start the recursion from, or C{None}
            to recurse the whole tree.
        @type branch: L{PyFFI.ObjectModels.Tree.GlobalTree}
        """
        # when called without arguments, recurse over the whole tree
        if branch is None:
            branch = self.data
        # the root data element: datainspect has already been called
        if branch is self.data:
            self.toaster.msgblockbegin(
                "--- %s ---" % self.SPELLNAME)
            if self.dataentry():
                # spell returned True so recurse to children
                # we use the abstract tree functions to parse the tree
                # these are format independent!
                for i in xrange(branch.getGlobalTreeNumChildren()):
                    child = branch.getGlobalTreeChild(i)
                    self.recurse(child)
                self.dataexit()
            self.toaster.msgblockend()
        elif self._branchinspect(branch) and self.branchinspect(branch):
            self.toaster.msgblockbegin(
                """~~~ %s [%s] ~~~"""
                % (branch.__class__.__name__,
                   branch.getGlobalNodeDataDisplay()))
            # cast the spell on the branch
            if self.branchentry(branch):
                # spell returned True so recurse to children
                # we use the abstract tree functions to parse the tree
                # these are format independent!
                for i in xrange(branch.getGlobalTreeNumChildren()):
                    child = branch.getGlobalTreeChild(i)
                    self.recurse(child)
                self.branchexit(branch)
            self.toaster.msgblockend()

    def dataentry(self):
        """Called before all blocks are recursed.
        The default implementation simply returns C{True}.
        You can access the data via C{self.L{data}}, and unlike in the
        L{datainspect} method, the full file has been processed at this stage.

        Typically, you will override this function to perform a global
        operation on the file data.

        @return: C{True} if the children must be processed, C{False} otherwise.
        @rtype: C{bool}
        """
        return True

    def branchentry(self, branch):
        """Cast the spell on the given branch. First called with branch equal to
        L{data}'s children, then the grandchildren, and so on.
        The default implementation simply returns C{True}.

        Typically, you will override this function to perform an operation
        on a particular block type and/or to stop recursion at particular
        block types.

        @param branch: The branch to cast the spell on.
        @type branch: L{PyFFI.ObjectModels.Tree.GlobalTree}
        @return: C{True} if the children must be processed, C{False} otherwise.
        @rtype: C{bool}
        """
        return True

    def branchexit(self, branch):
        """Cast a spell on the given branch, after all its children,
        grandchildren, have been processed, if L{branchentry} returned
        C{True} on the given branch.

        Typically, you will override this function to perform a particular
        operation on a block type, but you rely on the fact that the children
        must have been processed first.

        @param branch: The branch to cast the spell on.
        @type branch: L{PyFFI.ObjectModels.Tree.GlobalTree}
        """
        pass

    def dataexit(self):
        """Called after all blocks have been processed, if L{dataentry}
        returned C{True}.

        Typically, you will override this function to perform a final spell
        operation, such as writing back the file in a special way, or making a
        summary log.
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

class SpellGroupBase(Spell):
    """Base class for grouping spells. This implements all the spell grouping
    functions that fall outside of the actual recursing (L{__init__},
    L{toastentry}, L{_datainspect}, L{datainspect}, and L{toastexit}).

    @cvar SPELLCLASSES: List of spells of this group.
    @type SPELLCLASSES: C{list} of C{type(L{Spell})}
    @cvar ACTIVESPELLCLASSES: List of active spells of this
        groups. This list is automatically built when L{toastentry} is
        called.
    @type ACTIVESPELLCLASSES: C{list} of C{type(L{Spell})}
    @ivar spells: List of active spell instances.
    @type spells: C{list} of L{Spell}
    """
    SPELLCLASSES = []
    ACTIVESPELLCLASSES = []

    def __init__(self, toaster, data, stream):
        """Initialize the spell data for all given spells.

        @param toaster: The toaster this spell is called from.
        @type toaster: L{Toaster}
        @param data: The file data.
        @type data: L{PyFFI.ObjectModels.FileFormat.FileFormat.Data}
        @param stream: The file stream.
        @type stream: C{file}
        """
        # call base class constructor
        Spell.__init__(self, toaster=toaster, data=data, stream=stream)
        # set up the list of spells
        self.spells = [spellclass(toaster=toaster, data=data, stream=stream)
                       for spellclass in self.ACTIVESPELLCLASSES]

    def datainspect(self):
        """Inspect every spell with L{Spell.datainspect} and keep
        those spells that must be cast."""
        self.spells = [spell for spell in self.spells
                       if spell.datainspect()]
        return bool(self.spells)

    @classmethod
    def toastentry(cls, toaster):
        cls.ACTIVESPELLCLASSES = [
            spellclass for spellclass in cls.SPELLCLASSES
            if spellclass.toastentry(toaster)]
        return bool(cls.ACTIVESPELLCLASSES)

    @classmethod
    def toastexit(cls, toaster):
        for spellclass in cls.ACTIVESPELLCLASSES:
            spellclass.toastexit(toaster)

class SpellGroupSeriesBase(SpellGroupBase):
    """Base class for running spells in series."""
    def recurse(self, branch=None):
        """Recurse spells in series."""
        for spell in self.spells:
            spell.recurse(branch)

    # the following functions must NEVER be called in series of spells
    # everything is handled by the recurse function

    def branchinspect(self, branch):
        raise RuntimeError("use recurse")

    def branchentry(self, branch):
        raise RuntimeError("use recurse")

    def dataexit(self):
        raise RuntimeError("use recurse")

    def dataentry(self):
        raise RuntimeError("use recurse")

    def dataexit(self):
        raise RuntimeError("use recurse")

class SpellGroupParallelBase(SpellGroupBase):
    """Base class for running spells in parallel (that is, with only
    a single recursion in the tree).
    """
    def branchinspect(self, branch):
        """Inspect spells with L{Spell.branchinspect} (not all checks are
        executed, only keeps going until a spell inspection returns C{True}).
        """
        return any(spell.branchinspect(branch) for spell in self.spells)

    def branchentry(self, branch):
        """Run all spells."""
        # not using any: we want all entry code to be executed
        return bool([spell.branchentry(branch) for spell in self.spells])

    def branchexit(self, branch):
        for spell in self.spells:
             spell.branchexit(branch)

    def dataentry(self):
        """Look into every spell with L{Spell.dataentry}."""
        self.spells = [spell for spell in self.spells
                       if spell.dataentry()]
        return bool(self.spells)

    def dataexit(self):
        """Look into every spell with L{Spell.dataexit}."""
        for spell in self.spells:
            spell.dataexit()

def SpellGroupSeries(*args):
    """Class factory for grouping spells in series."""
    return type("".join(spellclass.__name__ for spellclass in args),
                (SpellGroupSeriesBase,),
                {"SPELLCLASSES": args,
                 "SPELLNAME":
                     " | ".join(spellclass.SPELLNAME for spellclass in args),
                 "READONLY": 
                      all(spellclass.READONLY for spellclass in args)})

def SpellGroupParallel(*args):
    """Class factory for grouping spells in parallel."""
    return type("".join(spellclass.__name__ for spellclass in args),
                (SpellGroupParallelBase,),
                {"SPELLCLASSES": args,
                 "SPELLNAME":
                     " & ".join(spellclass.SPELLNAME for spellclass in args),
                 "READONLY": 
                      all(spellclass.READONLY for spellclass in args)})

class SpellApplyPatch(Spell):
    """A spell for applying a patch on files."""

    SPELLNAME = "applypatch"

    def datainspect(self):
        """There is no need to read the whole file, so we apply the patch
        already at inspection stage, and stop the spell process by returning
        C{False}.
    
        @return: C{False}
        @rtype: C{bool}
        """
        # get the patch command (if there is one)
        patchcmd = self.toaster.options.get("patchcmd")
        # first argument is always the stream, by convention
        oldfile = self.stream
        oldfilename = oldfile.name
        newfilename = oldfilename + ".patched"
        patchfilename = oldfilename + ".patch"
        self.toaster.msg("writing %s..." % newfilename)
        if not patchcmd:
            patchfile = open(patchfilename, "rb")
            newfile = open(newfilename, "wb")
            try:
                PyFFI.Utils.BSDiff.patch(oldfile, newfile, patchfile)
            finally:
                newfile.close()
                patchfile.close()
        else:
            # close all files before calling external command
            oldfile.close()
            subprocess.call([patchcmd, oldfilename, newfilename, patchfilename])

        # do not go further, spell is done
        return False

class _MetaCompatSpell(type):
    """Metaclass for compatibility spell factory."""
    def __init__(cls, name, bases, dct):
        # create the derived class
        super(_MetaCompatSpell, cls).__init__(name, bases, dct)
        # set readonly class variable
        cls.READONLY = getattr(cls.SPELLMODULE, "__readonly__", True)
        # spell name is the last component of the name of the module
        cls.SPELLNAME = cls.SPELLMODULE.__name__.split(".")[-1]
        # set documentation
        cls.__doc__ = getattr(cls.SPELLMODULE, "__doc__", "Undocumented.")

class _CompatSpell(Spell):
    """This is a spell class that can be instantiated from an
    old-style spell module. DO NOT USE FOR NEW SPELLS! Only for
    backwards compatibility with the nif spells.
    """
    SPELLMODULE = type("spellmod", (object,), {}) # stub
    __metaclass__ = _MetaCompatSpell

    def branchinspect(self, branch):
        return hasattr(self.SPELLMODULE, "testBlock")

    def dataentry(self):
        # the beginning; start with testing the roots
        if hasattr(self.SPELLMODULE, "testRoot"):
            for i in xrange(self.data.getGlobalTreeNumChildren()):
                # the roots in the old system are children of data root
                root = self.data.getGlobalTreeChild(i)
                self.SPELLMODULE.testRoot(root, **self.toaster.options)
        # continue recursion
        return True

    def branchentry(self, branch):
        # test the block
        self.SPELLMODULE.testBlock(branch, **self.toaster.options)
        # continue recursion
        return True

    def dataexit(self):
        """Calls the testFile function."""
        if hasattr(self.SPELLMODULE, "testFile"):
            self.SPELLMODULE.testFile(
                self.stream,
                self.data.version, self.data.user_version,
                self.data.roots,
                **self.toaster.options)

def CompatSpellFactory(spellmod):
    """Create new-style spell class from old-style spell module.

    @param spellmod: The old-style spell module.
    @type spellmod: C{ModuleType}
    @return: The new-style spell class.
    @rtype: C{type(L{Spell})}
    """
    return type(spellmod.__name__.split(".")[-1], (_CompatSpell,),
                {"SPELLMODULE": spellmod})

class _MetaCompatToaster(type):
    """Metaclass for L{Toaster} which converts old-style module spells into
    new-style class spells.

    This is only for temporary use until all spells have been converted to
    the new class system.
    """

    def __init__(cls, name, bases, dct):
        """Check the list of spells, and convert old-style modules to new-style
        classes."""
        super(_MetaCompatToaster, cls).__init__(name, bases, dct)
        for i, spellclass in enumerate(cls.SPELLS):
            if isinstance(spellclass, ModuleType):
                cls.SPELLS[i] = CompatSpellFactory(spellclass)

class Toaster(object):
    """Toaster base class. Toasters run spells on large quantities of files.
    They load each file and pass the data structure to any number of spells.

    @cvar FILEFORMAT: The file format class.
    @type FILEFORMAT: C{type(L{FileFormat})}
    @cvar SPELLS: List of all available spell classes.
    @type SPELLS: C{list} of C{type(L{Spell})}
    @cvar EXAMPLES: Description of example use.
    @type EXAMPLES: C{str}
    @cvar ALIASDICT: Dictionary with aliases for spells.
    @type ALIASDICT: C{dict}
    @ivar spellclasses: List of spell classes for the particular instance (must
        be a subset of L{SPELLS}).
    @type spellclasses: C{list} of C{type(L{Spell})}
    @ivar options: The options of the toaster.
    @type options: C{dict}
    @ivar indent: Current level of indentation for messages.
    @type indent: C{int}
    @ivar logstream: File where to write output to (default is C{sys.stdout}).
    @type logstream: C{file}
    @ivar include_types: Tuple of types corresponding to C{options.include}.
    @type include_types: C{tuple}
    @ivar exclude_types: Tuple of types corresponding to C{options.exclude}.
    @type exclude_types: C{tuple}
    """

    FILEFORMAT = PyFFI.ObjectModels.FileFormat.FileFormat # override
    SPELLS = [] # override when subclassing
    EXAMPLES = "" # override when subclassing
    ALIASDICT = {} # override when subclassing

    __metaclass__ = _MetaCompatToaster # for compatibility

    def __init__(self, spellclass=None, options=None, logstream=None):
        """Initialize the toaster.

        @param spellclass: The spell class.
        @type spellclass: C{type(L{Spell})}
        @param options: The options (as keyword arguments).
        @type options: C{dict}
        @param logstream: Where to write the log (default is C{sys.stdout}).
        @type logstream: C{file}
        """
        self.spellclass = spellclass
        self.options = options if options else {}
        self.indent = 0
        self.logstream = sys.stdout if logstream is None else logstream
        # get list of block types that are included and excluded
        # these are used on branch checks
        self.include_types = tuple(
            getattr(self.FILEFORMAT, block_type)
            for block_type in self.options.get("include", ()))
        self.exclude_types = tuple(
            getattr(self.FILEFORMAT, block_type)
            for block_type in self.options.get("exclude", ()))

    def msg(self, message, level=0):
        """Write message to the L{logstream}, if verbosity is at least the
        given level. The default level is 0. If verbosity is not defined,
        then it is assumed to be -1, that is, the function does not print
        anything.

        @param message: The message to write.
        @type message: C{str}
        @param level: Verbosity level of the message. The message is only
            logged if C{L{options}["verbose"]} is at least this value. Must
            be non-negative.
        @type level: C{int}
        """
        # check level
        if level < 0:
            raise ValueError("message level must be non-negative")
        # if verbosity is not defined, use -1: never print anything
        if level <= self.options.get("verbose", -1):
            for line in message.split("\n"):
                print >>self.logstream, "  " * self.indent + line

    def msgblockbegin(self, message, level=0):
        """Acts like L{msg}, but also increases L{indent} after writing the
        message."""
        self.msg(message, level)
        self.indent += 1

    def msgblockend(self, message=None, level=0):
        """Acts like L{msg}, but also decreases L{indent} before writing the
        message, but if the message argument is C{None}, then no message is
        printed."""
        self.indent -= 1
        if not(message is None):
            self.msg(message, level)

    def isadmissiblebranchtype(self, branchtype):
        """Helper function which checks whether a given branch type should
        have spells cast on it or not, based in exclude and include options.

        >>> from PyFFI.Formats.NIF import NifFormat
        >>> class MyToaster(Toaster):
        ...     FILEFORMAT = NifFormat
        >>> toaster = MyToaster() # no include or exclude: all admissible
        >>> toaster.isadmissiblebranchtype(NifFormat.NiProperty)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiNode)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiAVObject)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiLODNode)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiMaterialProperty)
        True
        >>> toaster = MyToaster(options={"exclude": ["NiProperty", "NiNode"]})
        >>> toaster.isadmissiblebranchtype(NifFormat.NiProperty)
        False
        >>> toaster.isadmissiblebranchtype(NifFormat.NiNode)
        False
        >>> toaster.isadmissiblebranchtype(NifFormat.NiAVObject)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiLODNode)
        False
        >>> toaster.isadmissiblebranchtype(NifFormat.NiMaterialProperty)
        False
        >>> toaster = MyToaster(options={"include": ["NiProperty", "NiNode"]})
        >>> toaster.isadmissiblebranchtype(NifFormat.NiProperty)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiNode)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiAVObject)
        False
        >>> toaster.isadmissiblebranchtype(NifFormat.NiLODNode) # NiNodes are!
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiMaterialProperty) # NiProperties are!
        True
        >>> toaster = MyToaster(options={"include": ["NiProperty", "NiNode"], "exclude": ["NiMaterialProperty", "NiLODNode"]})
        >>> toaster.isadmissiblebranchtype(NifFormat.NiProperty)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiNode)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiAVObject)
        False
        >>> toaster.isadmissiblebranchtype(NifFormat.NiLODNode)
        False
        >>> toaster.isadmissiblebranchtype(NifFormat.NiSwitchNode)
        True
        >>> toaster.isadmissiblebranchtype(NifFormat.NiMaterialProperty)
        False
        >>> toaster.isadmissiblebranchtype(NifFormat.NiAlphaProperty)
        True
        """
        #print("checking %s" % branchtype.__name__) # debug
        # check that block is not in exclude...
        if not issubclass(branchtype, self.exclude_types):
            # not excluded!
            # check if it is included
            if not self.include_types:
                # if no include list is given, then assume included by default
                # so, the block is admissible
                return True
            elif issubclass(branchtype, self.include_types):
                # included as well! the block is admissible
                return True
        # not admissible
        #print("not admissible") # debug
        return False

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
        parser.add_option("--series", dest="series",
                          action="store_true",
                          help="run spells in series rather than in parallel")
        parser.set_defaults(raisetesterror=False, verbose=1, pause=False,
                            exclude=[], include=[], examples=False,
                            spells=False,
                            #raisereaderror=True, ### no longer used
                            interactive=True,
                            helpspell=False, dryrun=False, prefix="", arg="",
                            createpatch=False, applypatch=False, diffcmd="",
                            series=False)
        (options, args) = parser.parse_args()

        # convert options to dictionary
        self.options = {}
        for optionname in dir(options):
            # skip default attributes of optparse.Values
            if not optionname in dir(optparse.Values):
                self.options[optionname] = getattr(options, optionname)

        # update include and exclude types
        self.include_types = tuple(
            getattr(self.FILEFORMAT, block_type)
            for block_type in self.options.get("include", ()))
        self.exclude_types = tuple(
            getattr(self.FILEFORMAT, block_type)
            for block_type in self.options.get("exclude", ()))

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
                self.msg(spellclass.SPELLNAME)
            return
        if options.examples:
            self.msg(self.EXAMPLES)
            return

        # spell name not specified when function was called
        if len(args) < 1:
            parser.error(errormessage_numargs)

        # check if we are applying patches
        if options.applypatch:
            if len(args) > 1:
                parser.error("when using --patch, do not specify a spell")
            # set spell class to applying patch
            self.spellclass = SpellApplyPatch
        else:
            # get spell names
            spellnames = args[:-1]
            # get spell classes
            spellclasses = []
            for spellname in spellnames:
                # convert old names
                if spellname in self.ALIASDICT:
                    print("""\
WARNING: the %s spell is deprecated
         and will be removed from a future release
         use the %s spell as a replacement"""
                          % (spellname, self.ALIASDICT[spellname]))
                    spellname = self.ALIASDICT[spellname]
                # find the spell
                spellklasses = [spellclass for spellclass in self.SPELLS
                                if spellclass.SPELLNAME == spellname]
                if not spellklasses:
                    parser.error("%s is not a known spell" % spellname)
                if len(spellklasses) > 1:
                    parser.error("multiple spells are called %s (BUG?)"
                                 % spellname)
                spellclasses.extend(spellklasses)
            # create group of spells
            if len(spellclasses) > 1:
                if options.series:
                    self.spellclass = SpellGroupSeries(*spellclasses)
                else:
                    self.spellclass = SpellGroupParallel(*spellclasses)
            else:
                self.spellclass = spellclasses[0]

            if options.helpspell:
                # TODO: format the docstring
                self.msg(self.spellclass.__doc__)
                return

            # top not specified when function was called
            if len(args) < 2:
                parser.error(errormessage_numargs)

        # get top folder/file: last argument always is folder/file
        top = args[-1]

        self.toast(top)

        # signal the end
        if options.pause and options.interactive:
            raw_input("Finished.")
        else:
            print("Finished.")

    def toast(self, top):
        """Walk over all files in a directory tree and cast spells
        on every file.

        @param top: The directory or file to toast.
        @type top: str
        """

        # toast entry code
        if not self.spellclass.toastentry(self):
            self.msg("spell does not apply! quiting early...")
            return

        ### raisereaderror is ignored in this implementation!!!
        ### new-style toaster has it functionally equal to
        ### raisetesterror
        #raisereaderror = self.options.get("raisereaderror", True)

        # some defaults are different from the defaults defined in
        # the cli function: these defaults are reasonable for when the
        # toaster is called NOT from the command line
        # whereas the cli function defines defaults that are reasonable
        # when the toaster is called from the command line
        # in particular, when calling from the command line, the script
        # is much more verbose by default

        # default verbosity is -1: do not print anything (!= cli default)
        verbose = self.options.get("verbose", -1)

        # raise test errors by default so caller can know what happened
        # (!= cli default)
        raisetesterror = self.options.get("raisetesterror", True)

        pause = self.options.get("pause", False)

        # do not ask for confirmation (!= cli default)
        interactive = self.options.get("interactive", False)

        dryrun = self.options.get("dryrun", False)
        prefix = self.options.get("prefix", "")
        createpatch = self.options.get("createpatch", False)
        applypatch = self.options.get("applypatch", False)

        # warning
        if ((not self.spellclass.READONLY) and (not dryrun)
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

        # walk over all streams, and create a data instance for each of them
        # inspect the file but do not yet read in full
        for stream, data in self.FILEFORMAT.walkData(
            top, mode='rb' if self.spellclass.READONLY else 'r+b'):

            try: 
                self.msgblockbegin("=== %s ===" % stream.name)

                # inspect the file (reads only the header)
                data.inspect(stream)
 
                # create spell instance
                spell = self.spellclass(toaster=self, data=data, stream=stream)
                
                # inspect the spell instance
                if spell._datainspect() and spell.datainspect():
                    # read the full file
                    data.read(stream)
                    
                    # cast the spell on the data tree
                    spell.recurse()

                    # save file back to disk if not readonly
                    if not self.spellclass.READONLY:
                        if not dryrun:
                            if createpatch:
                                self.writepatch(stream, data)
                            elif prefix:
                                self.writeprefix(stream, data)
                            else:
                                self.writeover(stream, data)
                        else:
                            # write back to a temporary file
                            self.writetemp(stream, data)

                # force free memory (helps when parsing many very large files)
                del spell
                gc.collect()

            except StandardError:
                print("""\
*** TEST FAILED ON %-51s ***
*** If you were running a spell that came with PyFFI, then             ***
*** please report this as a bug (include the file) on                  ***
*** http://sourceforge.net/tracker/?group_id=199269                    ***
""" % stream.name)
                # if raising test errors, reraise the exception
                if raisetesterror:
                    raise
            finally:
                self.msgblockend()

        # toast exit code
        self.spellclass.toastexit(self)

    def writetemp(self, stream, data):
        """Writes the data to a temporary file and raises an exception if the
        write fails.
        """
        self.msg("writing to temporary file")
        outstream = tempfile.TemporaryFile()
        try:
            try:
                data.write(outstream)
            except StandardError:
                self.msg("write failed!!!")
                raise
        finally:
            outstream.close()

    def writeprefix(self, stream, data):
        """Writes the data to a file, appending a prefix to the original file
        name.
        """
        # first argument is always the stream, by convention
        head, tail = os.path.split(stream.name)
        outstream = open(os.path.join(head, self.options["prefix"] + tail),
                         "wb")
        try:
            self.msg("writing %s" % outstream.name)
            try:
                data.write(outstream)
            except StandardError:
                self.msg("write failed!!!")
                raise
        finally:
            outstream.close()

    def writeover(self, stream, data):
        """Overwrites original file with data, but restores file if fails."""
        # first argument is always the stream, by convention
        stream.seek(0)
        backup = stream.read(-1)
        stream.seek(0)
        self.msg("writing %s" % stream.name)
        try:
            data.write(stream)
        except: # not just StandardError, also CTRL-C
            self.msg("write failed!!! attempting to restore original file...")
            stream.seek(0)
            stream.write(backup)
            stream.truncate()
            raise
        stream.truncate()

    def writepatch(self, stream, data):
        """Creates a binary patch for the updated file."""
        diffcmd = self.options.get('diffcmd')
        # create a temporary file that won't get deleted when closed
        newfile = tempfile.NamedTemporaryFile()
        newfilename = newfile.name
        newfile.close()
        newfile = open(newfilename, "w+b")
        self.msg("writing to temporary file")
        try:
            data.write(newfile)
        except: # not just StandardError, also CTRL-C
            self.msg("write failed!!!")
            raise
        if not diffcmd:
            # use internal differ
            oldfile = stream
            oldfile.seek(0)
            newfile.seek(0)
            patchfile = open(oldfile.name + ".patch", "wb")
            self.msg("writing patch")
            PyFFI.Utils.BSDiff.diff(oldfile, newfile, patchfile)
            patchfile.close()
            newfile.close()
        else:
            # use external diff command
            oldfile = stream
            oldfilename = oldfile.name
            patchfilename = oldfilename + ".patch"
            # close all files before calling external command
            oldfile.close()
            newfile.close()
            self.msg("calling %s" % diffcmd)
            subprocess.call([diffcmd, oldfilename, newfilename, patchfilename])
        # delete temporary file
        os.remove(newfilename)

###########################
### OLD DEPRECATED CODE ###
###########################

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

