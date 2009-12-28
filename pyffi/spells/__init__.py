"""
:mod:`pyffi.spells` --- High level file operations
==================================================

.. note::
   
   This module is based on wz's NifTester module, although
   nothing of wz's original code is left in this module.

A :term:`toaster`, implemented by subclasses of the abstract
:class:`Toaster` class, walks over all files in a folder, and applies
one or more transformations on each file. Such transformations are
called :term:`spell`\ s, and are implemented by subclasses of the
abstract :class:`Spell` class.

A :term:`spell` can also run independently of a :term:`toaster` and be
applied on a branch directly. The recommended way of doing this is via
the :meth:`Spell.recurse` method.

Supported spells
----------------

For format specific spells, refer to the corresponding module.

.. toctree::
   :maxdepth: 2
   
   pyffi.spells.cgf
   pyffi.spells.dae
   pyffi.spells.dds
   pyffi.spells.kfm
   pyffi.spells.nif
   pyffi.spells.tga

Some spells are applicable on every file format, and those are documented
here.

.. autoclass:: SpellApplyPatch
   :show-inheritance:
   :members:

Adding new spells
-----------------

To create new spells, derive your custom spells from the :class:`Spell`
class, and include them in the :attr:`Toaster.SPELLS` attribute of your
toaster.

.. autoclass:: Spell
   :show-inheritance:
   :members: READONLY, SPELLNAME, data, stream, toaster,
             __init__, recurse, _datainspect, datainspect, _branchinspect,
             branchinspect, dataentry, dataexit, branchentry,
             branchexit, toastentry, toastexit

Grouping spells together
------------------------

It is also possible to create composite spells, that is, spells that
simply execute other spells. The following functions and classes can
be used for this purpose.

.. autofunction:: SpellGroupParallel

.. autofunction:: SpellGroupSeries

.. autoclass:: SpellGroupBase
   :show-inheritance:
   :members:
   :undoc-members:
   

.. autoclass:: SpellGroupParallelBase
   :show-inheritance:
   :members:
   :undoc-members:
   

.. autoclass:: SpellGroupSeriesBase
   :show-inheritance:
   :members:
   :undoc-members:

Creating toaster scripts
------------------------

To create a new toaster script, derive your toaster from the :class:`Toaster`
class, and set the :attr:`Toaster.FILEFORMAT` attribute of your toaster to
the file format class of the files it can toast.

.. autoclass:: Toaster
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

"""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, Python File Format Interface
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

from copy import deepcopy
from cStringIO import StringIO
import gc
import logging # Logger
try:
    import multiprocessing # Pool
except ImportError:
    # < py26
    multiprocessing = None
import optparse
import os
import os.path
import re # for regex parsing (--skip, --only)
import subprocess
import sys # sys.stdout
import tempfile

import pyffi # for pyffi.__version__
import pyffi.object_models # pyffi.object_models.FileFormat

class Spell(object):
    """Spell base class. A spell takes a data file and then does something
    useful with it. The main entry point for spells is :meth:`recurse`, so if you
    are writing new spells, start with reading the documentation with
    :meth:`recurse`.
    """

    data = None
    """The :class:`~pyffi.object_models.FileFormat.Data` instance
    this spell acts on."""

    stream = None
    """The current ``file`` being processed."""

    toaster = None
    """The :class:`Toaster` instance this spell is called from."""

    # spells are readonly by default
    READONLY = True
    """A ``bool`` which determines whether the spell is read only or
    not. Default value is ``True``. Override this class attribute, and
    set to ``False``, when subclassing a spell that must write files
    back to the disk.
    """

    SPELLNAME = None
    """A ``str`` describing how to refer to the spell from the command line.
    Override this class attribute when subclassing.
    """

    def __init__(self, toaster=None, data=None, stream=None):
        """Initialize the spell data.

        :param data: The file :attr:`data`.
        :type data: :class:`~pyffi.object_models.FileFormat.Data`
        :param stream: The file :attr:`stream`.
        :type stream: ``file``
        :param toaster: The :attr:`toaster` this spell is called from (optional).
        :type toaster: :class:`Toaster`
        """
        self.data = data
        self.stream = stream
        self.toaster = toaster if toaster else Toaster()

    def _datainspect(self):
        """This is called after :meth:`pyffi.object_models.FileFormat.Data.inspect` has
        been called, and before :meth:`pyffi.object_models.FileFormat.Data.read` is
        called.

        :return: ``True`` if the file must be processed, ``False`` otherwise.
        :rtype: ``bool``
        """
        # for the moment, this does nothing
        return True

    def datainspect(self):
        """This is called after :meth:`pyffi.object_models.FileFormat.Data.inspect` has
        been called, and before :meth:`pyffi.object_models.FileFormat.Data.read` is
        called. Override this function for customization.

        :return: ``True`` if the file must be processed, ``False`` otherwise.
        :rtype: ``bool``
        """
        # for nif: check if version applies, or
        # check if spell block type is found
        return True

    def _branchinspect(self, branch):
        """Check if spell should be cast on this branch or not, based on
        exclude and include options passed on the command line. You should
        not need to override this function: if you need additional checks on
        whether a branch must be parsed or not, override the :meth:`branchinspect`
        method.

        :param branch: The branch to check.
        :type branch: :class:`~pyffi.utils.graph.GlobalNode`
        :return: ``True`` if the branch must be processed, ``False`` otherwise.
        :rtype: ``bool``
        """
        # fall back on the toaster implementation
        return self.toaster.is_admissible_branch_class(branch.__class__)

    def branchinspect(self, branch):
        """Like :meth:`_branchinspect`, but for customization: can be overridden to
        perform an extra inspection (the default implementation always
        returns ``True``).

        :param branch: The branch to check.
        :type branch: :class:`~pyffi.utils.graph.GlobalNode`
        :return: ``True`` if the branch must be processed, ``False`` otherwise.
        :rtype: ``bool``
        """
        return True

    def recurse(self, branch=None):
        """Helper function which calls :meth:`_branchinspect` and :meth:`branchinspect`
        on the branch,
        if both successful then :meth:`branchentry` on the branch, and if this is
        succesful it calls :meth:`recurse` on the branch's children, and
        once all children are done, it calls :meth:`branchexit`.

        Note that :meth:`_branchinspect` and :meth:`branchinspect` are not called upon
        first entry of this function, that is, when called with :attr:`data` as
        branch argument. Use :meth:`datainspect` to stop recursion into this branch.

        Do not override this function.

        :param branch: The branch to start the recursion from, or ``None``
            to recurse the whole tree.
        :type branch: :class:`~pyffi.utils.graph.GlobalNode`
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
                for child in branch.get_global_child_nodes():
                    self.recurse(child)
                self.dataexit()
            self.toaster.msgblockend()
        elif self._branchinspect(branch) and self.branchinspect(branch):
            self.toaster.msgblockbegin(
                """~~~ %s [%s] ~~~"""
                % (branch.__class__.__name__,
                   branch.get_global_display()))
            # cast the spell on the branch
            if self.branchentry(branch):
                # spell returned True so recurse to children
                # we use the abstract tree functions to parse the tree
                # these are format independent!
                for child in branch.get_global_child_nodes():
                    self.recurse(child)
                self.branchexit(branch)
            self.toaster.msgblockend()

    def dataentry(self):
        """Called before all blocks are recursed.
        The default implementation simply returns ``True``.
        You can access the data via :attr:`data`, and unlike in the
        :meth:`datainspect` method, the full file has been processed at this stage.

        Typically, you will override this function to perform a global
        operation on the file data.

        :return: ``True`` if the children must be processed, ``False`` otherwise.
        :rtype: ``bool``
        """
        return True

    def branchentry(self, branch):
        """Cast the spell on the given branch. First called with branch equal to
        :attr:`data`'s children, then the grandchildren, and so on.
        The default implementation simply returns ``True``.

        Typically, you will override this function to perform an operation
        on a particular block type and/or to stop recursion at particular
        block types.

        :param branch: The branch to cast the spell on.
        :type branch: :class:`~pyffi.utils.graph.GlobalNode`
        :return: ``True`` if the children must be processed, ``False`` otherwise.
        :rtype: ``bool``
        """
        return True

    def branchexit(self, branch):
        """Cast a spell on the given branch, after all its children,
        grandchildren, have been processed, if :meth:`branchentry` returned
        ``True`` on the given branch.

        Typically, you will override this function to perform a particular
        operation on a block type, but you rely on the fact that the children
        must have been processed first.

        :param branch: The branch to cast the spell on.
        :type branch: :class:`~pyffi.utils.graph.GlobalNode`
        """
        pass

    def dataexit(self):
        """Called after all blocks have been processed, if :meth:`dataentry`
        returned ``True``.

        Typically, you will override this function to perform a final spell
        operation, such as writing back the file in a special way, or making a
        summary log.
        """
        pass

    @classmethod
    def toastentry(cls, toaster):
        """Called just before the toaster starts processing
        all files. If it returns ``False``, then the spell is not used.
        The default implementation simply returns ``True``.

        For example, if the spell only acts on a particular block type, but
        that block type is excluded, then you can use this function to flag
        that this spell can be skipped. You can also use this function to
        initialize statistics data to be aggregated from files, to
        initialize a log file, and so.

        :param toaster: The toaster this spell is called from.
        :type toaster: :class:`Toaster`
        :return: ``True`` if the spell applies, ``False`` otherwise.
        :rtype: ``bool``
        """
        return True

    @classmethod
    def toastexit(cls, toaster):
        """Called when the toaster has finished processing
        all files.

        :param toaster: The toaster this spell is called from.
        :type toaster: :class:`Toaster`
        """
        pass

class SpellGroupBase(Spell):
    """Base class for grouping spells. This implements all the spell grouping
    functions that fall outside of the actual recursing (:meth:`__init__`,
    :meth:`toastentry`, :meth:`_datainspect`, :meth:`datainspect`, and :meth:`toastexit`).
    """

    SPELLCLASSES = []
    """List of :class:`Spell`\ s of this group (not instantiated)."""

    ACTIVESPELLCLASSES = []
    """List of active spells of this group (not instantiated).
    This list is automatically built when :meth:`toastentry` is called.
    """

    spells = []
    """List of active spell instances."""

    def __init__(self, toaster, data, stream):
        """Initialize the spell data for all given spells.

        :param toaster: The toaster this spell is called from.
        :type toaster: :class:`Toaster`
        :param data: The file data.
        :type data: :class:`pyffi.object_models.FileFormat.Data`
        :param stream: The file stream.
        :type stream: ``file``
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
        """Inspect spells with :meth:`Spell.branchinspect` (not all checks are
        executed, only keeps going until a spell inspection returns ``True``).
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
        """Look into every spell with :meth:`Spell.dataentry`."""
        self.spells = [spell for spell in self.spells
                       if spell.dataentry()]
        return bool(self.spells)

    def dataexit(self):
        """Look into every spell with :meth:`Spell.dataexit`."""
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
        ``False``.
    
        :return: ``False``
        :rtype: ``bool``
        """
        # get the patch command (if there is one)
        patchcmd = self.toaster.options["patchcmd"]
        if not patchcmd:
            raise ValueError("must specify a patch command")
        # first argument is always the stream, by convention
        oldfile = self.stream
        oldfilename = oldfile.name
        newfilename = oldfilename + ".patched"
        patchfilename = oldfilename + ".patch"
        self.toaster.msg("writing %s..." % newfilename)
        # close all files before calling external command
        oldfile.close()
        subprocess.call([patchcmd, oldfilename, newfilename, patchfilename])

        # do not go further, spell is done
        return False

def _toaster_multiprocessing(args):
    """For multiprocessing. This function creates a new toaster, with the
    given options and spells, and calls the toaster on filename.
    """
    toasterclass, filename, options, spellnames = args
    toaster = toasterclass(options=options, spellnames=spellnames)
    toaster.toast(filename)

class Toaster(object):
    """Toaster base class. Toasters run spells on large quantities of files.
    They load each file and pass the data structure to any number of spells.
    """

    FILEFORMAT = pyffi.object_models.FileFormat
    """The file format class (a subclass of
    :class:`~pyffi.object_models.FileFormat`)."""

    SPELLS = []
    """List of all available :class:`~pyffi.spells.Spell` classes."""

    EXAMPLES = ""
    """Some examples which describe typical use of the toaster."""

    ALIASDICT = {}
    """Dictionary with aliases for spells."""

    DEFAULT_OPTIONS = dict(
        raisetesterror=False, verbose=1, pause=False,
        exclude=[], include=[], examples=False,
        spells=False,
        interactive=True,
        helpspell=False, dryrun=False, prefix="", arg="",
        createpatch=False, applypatch=False, diffcmd="", patchcmd="",
        series=False,
        skip=[], only=[],
        multiprocessing=False)

    """List of spell classes of the particular :class:`Toaster` instance."""

    options = {}
    """The options of the toaster, as ``dict``."""

    spellnames = {}
    """A list of the names of the spells."""

    indent = 0
    """An ``int`` which describes the current indentation level for messages."""

    logger = logging.getLogger("pyffi.toaster")
    """A :class:`logging.Logger` for toaster log messages."""

    include_types = []
    """Tuple of types corresponding to the include key of :attr:`options`."""

    exclude_types = []
    """Tuple of types corresponding to the exclude key of :attr:`options`."""

    only_regexs = []
    """Tuple of regular expressions corresponding to the only key of
    :attr:`options`."""

    skip_regexs = []
    """Tuple of regular expressions corresponding to the skip key of
    :attr:`options`."""

    def __init__(self, spellclass=None, options=None, spellnames=None):
        """Initialize the toaster.

        :param spellclass: Deprecated, use spellnames.
        :type spellclass: :class:`Spell`
        :param options: The options (as keyword arguments).
        :type options: ``dict``
        :param spellnames: List of names of spells.
        :type spellnames: ``list`` of ``str``
        """
        self.options = deepcopy(self.DEFAULT_OPTIONS)
        self.spellnames = spellnames
        if options:
            self.options.update(options)
        self.indent = 0
        self.logger = logging.getLogger("pyffi.toaster")
        # update options and spell class
        self._update_options()
        if spellnames:
            self._update_spellclass()
        else:
            # deprecated
            self.spellclass = spellclass

    def _update_options(self):
        """Synchronize some fields with given options."""
        # set verbosity level
        if self.options["verbose"] <= 0:
            logging.getLogger("pyffi").setLevel(logging.WARNING)
        elif self.options["verbose"] == 1:
            logging.getLogger("pyffi").setLevel(logging.INFO)
        else:
            logging.getLogger("pyffi").setLevel(logging.DEBUG)
        # check errors
        if self.options["createpatch"] and self.options["applypatch"]:
            raise ValueError(
                "options --diff and --patch are mutually exclusive")
        if self.options["diffcmd"] and not(self.options["createpatch"]):
            raise ValueError(
                "option --diff-cmd can only be used with --diff")
        if self.options["patchcmd"] and not(self.options["applypatch"]):
            raise ValueError(
                "option --patch-cmd can only be used with --patch")
        if (multiprocessing is None) and self.options["multiprocessing"]:
            self.logger.warn(
                "multiprocessing not supported on this platform")
            self.options["multiprocessing"] = False
        # update include and exclude types
        self.include_types = tuple(
            getattr(self.FILEFORMAT, block_type)
            for block_type in self.options["include"])
        self.exclude_types = tuple(
            getattr(self.FILEFORMAT, block_type)
            for block_type in self.options["exclude"])
        # update skip and only regular expressions
        self.skip_regexs = tuple(
            re.compile(regex) for regex in self.options["skip"])
        self.only_regexs = tuple(
            re.compile(regex) for regex in self.options["only"])

    def _update_spellclass(self):
        """Update spell class from given list of spell names."""
        # get spell classes
        spellclasses = []
        for spellname in self.spellnames:
            # convert old names
            if spellname in self.ALIASDICT:
                self.logger.warning(
                    "The %s spell is deprecated and will be removed"
                    " from a future release; use the %s spell as a"
                    " replacement" % (spellname, self.ALIASDICT[spellname]))
                spellname = self.ALIASDICT[spellname]
            # find the spell
            spellklasses = [spellclass for spellclass in self.SPELLS
                            if spellclass.SPELLNAME == spellname]
            if not spellklasses:
                raise ValueError(
                    "%s is not a known spell" % spellname)
            if len(spellklasses) > 1:
                raise ValueError(
                    "multiple spells are called %s (BUG?)" % spellname)
            spellclasses.extend(spellklasses)
        # create group of spells
        if len(spellclasses) > 1:
            if self.options["series"]:
                self.spellclass = SpellGroupSeries(*spellclasses)
            else:
                self.spellclass = SpellGroupParallel(*spellclasses)
        else:
            self.spellclass = spellclasses[0]

    def msg(self, message):
        """Write log message with :meth:`logger.info`, taking into account
        :attr:`indent`.

        :param message: The message to write.
        :type message: ``str``
        """
        for line in message.split("\n"):
            self.logger.info("  " * self.indent + line)

    def msgblockbegin(self, message):
        """Acts like :meth:`msg`, but also increases :attr:`indent` after writing the
        message."""
        self.msg(message)
        self.indent += 1

    def msgblockend(self, message=None):
        """Acts like :meth:`msg`, but also decreases :attr:`indent` before writing the
        message, but if the message argument is ``None``, then no message is
        printed."""
        self.indent -= 1
        if not(message is None):
            self.msg(message)

    def is_admissible_branch_class(self, branchtype):
        """Helper function which checks whether a given branch type should
        have spells cast on it or not, based in exclude and include options.

        >>> from pyffi.formats.nif import NifFormat
        >>> class MyToaster(Toaster):
        ...     FILEFORMAT = NifFormat
        >>> toaster = MyToaster() # no include or exclude: all admissible
        >>> toaster.is_admissible_branch_class(NifFormat.NiProperty)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiNode)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiAVObject)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiLODNode)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiMaterialProperty)
        True
        >>> toaster = MyToaster(options={"exclude": ["NiProperty", "NiNode"]})
        >>> toaster.is_admissible_branch_class(NifFormat.NiProperty)
        False
        >>> toaster.is_admissible_branch_class(NifFormat.NiNode)
        False
        >>> toaster.is_admissible_branch_class(NifFormat.NiAVObject)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiLODNode)
        False
        >>> toaster.is_admissible_branch_class(NifFormat.NiMaterialProperty)
        False
        >>> toaster = MyToaster(options={"include": ["NiProperty", "NiNode"]})
        >>> toaster.is_admissible_branch_class(NifFormat.NiProperty)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiNode)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiAVObject)
        False
        >>> toaster.is_admissible_branch_class(NifFormat.NiLODNode) # NiNodes are!
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiMaterialProperty) # NiProperties are!
        True
        >>> toaster = MyToaster(options={"include": ["NiProperty", "NiNode"], "exclude": ["NiMaterialProperty", "NiLODNode"]})
        >>> toaster.is_admissible_branch_class(NifFormat.NiProperty)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiNode)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiAVObject)
        False
        >>> toaster.is_admissible_branch_class(NifFormat.NiLODNode)
        False
        >>> toaster.is_admissible_branch_class(NifFormat.NiSwitchNode)
        True
        >>> toaster.is_admissible_branch_class(NifFormat.NiMaterialProperty)
        False
        >>> toaster.is_admissible_branch_class(NifFormat.NiAlphaProperty)
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
        the command line, and run the :meth:`toast` method.
        """
        # parse options and positional arguments
        usage = "%prog [options] <spell1> <spell2> ... <file>|<folder>"
        description = (
            "Apply the spells <spell1>, <spell2>, and so on,"
            " on <file>, or recursively on <folder>.")
        errormessage_numargs = (
            "incorrect number of arguments (use the --help option for help)")

        parser = optparse.OptionParser(
            usage,
            version="%%prog (PyFFI %s)" % pyffi.__version__,
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
        parser.add_option("--skip", dest="skip",
                          type="string",
                          action="append",
                          metavar="SKIP",
                          help=
                          "skip all files whose names match the regular"
                          " expression SKIP (takes precedence over --only);"
                          " if specified multiple times, the expressions are"
                          " 'ored' together")
        parser.add_option("--only", dest="only",
                          type="string",
                          action="append",
                          metavar="ONLY",
                          help=
                          "only toast files whose names (i) match the"
                          " regular expression ONLY, and (ii) do not match"
                          " any regular expression specified with --skip;"
                          " if specified multiple times, the expressions are"
                          " 'ored' together; if not specified, all files"
                          " are toasted by default, except those listed"
                          " with --skip")
        parser.add_option(
            "--multiprocessing", dest="multiprocessing",
            action="store_true",
            help="enable multiprocessing")
        parser.set_defaults(**deepcopy(self.DEFAULT_OPTIONS))
        (options, args) = parser.parse_args()

        # convert options to dictionary
        self.options = {}
        for optionname in dir(options):
            # skip default attributes of optparse.Values
            if not optionname in dir(optparse.Values):
                self.options[optionname] = getattr(options, optionname)

        # update options
        self._update_options()

        # check if we had examples and/or spells: quit
        if options.spells:
            for spellclass in self.SPELLS:
                print(spellclass.SPELLNAME)
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
            self.spellclass = SpellApplyPatch
        else:
            # get spell names
            if options.helpspell:
                # special case: --spell-help would not have a path specified
                self.spellnames = args[:]
            else:
                self.spellnames = args[:-1]

            # update the spell class
            self._update_spellclass()

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
        self.logger.info("Finished.")
        if options.pause and options.interactive:
            raw_input("Press enter...")

    def inspect_filename(self, filename):
        """Returns whether to toast a filename or not, based on
        skip_regexs and only_regexs.
        """
        if any(regex.match(filename) for regex in self.skip_regexs):
            # matches some --skip regex, so do not toast
            return False
        if not self.only_regexs:
            # --only not specified: then by default we match all files
            return True
        if any(regex.match(filename) for regex in self.only_regexs):
            # matches at least one --only regex, so toast
            return True
        else:
            # no --only matches, so do not toast
            return False

    def toast(self, top):
        """Walk over all files in a directory tree and cast spells
        on every file.

        :param top: The directory or file to toast.
        :type top: str
        """

        # toast entry code
        if not self.spellclass.toastentry(self):
            self.msg("spell does not apply! quiting early...")
            return

        # some defaults are different from the defaults defined in
        # the cli function: these defaults are reasonable for when the
        # toaster is called NOT from the command line
        # whereas the cli function defines defaults that are reasonable
        # when the toaster is called from the command line
        # in particular, when calling from the command line, the script
        # is much more verbose by default

        # default verbosity is -1: do not show anything (!= cli default)
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
        enable_multiprocessing = self.options.get("multiprocessing", False)

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
                self.logger.info("Script aborted by user.")
                if pause:
                    raw_input("Press enter...")
                return

        # walk over all streams, and create a data instance for each of them
        # inspect the file but do not yet read in full
        if not enable_multiprocessing:
            for stream in self.FILEFORMAT.walk(
                top, mode='rb' if self.spellclass.READONLY else 'r+b'):
                pass # to set a breakpoint
                self._toast(stream)
                # force free memory (helps when parsing many very large files)
                gc.collect()
                pass # to set a breakpoint
        else:
            pool_options = deepcopy(self.options)
            pool_options["multiprocessing"] = False
            pool_options["interactive"] = False
            self.msg("toasting with %i threads" % multiprocessing.cpu_count())
            pool = multiprocessing.Pool()
            result = pool.map_async(
                _toaster_multiprocessing,
                ((self.__class__, filename, pool_options, self.spellnames)
                 for filename in pyffi.utils.walk(
                     top, onerror=None,
                     re_filename=self.FILEFORMAT.RE_FILENAME)))
            # specify timeout, so CTRL-C works
            # 99999999 is about 3 years, should be long enough... :-)
            result.get(timeout=99999999)

        # toast exit code
        self.spellclass.toastexit(self)

    def _toast(self, stream):
        """Run toaster on particular stream and data.
        Used as helper function.
        """
        # inspect the file name
        if not self.inspect_filename(stream.name):
            self.msg("=== %s (skipped) ===" % stream.name)
            return

        dryrun = self.options.get("dryrun", False)
        prefix = self.options.get("prefix", "")
        createpatch = self.options.get("createpatch", False)
        applypatch = self.options.get("applypatch", False)
        raisetesterror = self.options.get("raisetesterror", True)

        data = self.FILEFORMAT.Data()

        self.msgblockbegin("=== %s ===" % stream.name)
        try:
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

        except Exception:
            self.logger.error("TEST FAILED ON %s" % stream.name)
            self.logger.error(
                "If you were running a spell that came with PyFFI, then")
            self.logger.error(
                "please report this as a bug (include the file) on")
            self.logger.error(
                "http://sourceforge.net/tracker/?group_id=199269")
            # if raising test errors, reraise the exception
            if raisetesterror:
                raise
        finally:
            self.msgblockend()

    def writetemp(self, stream, data):
        """Writes the data to a temporary file and raises an exception if the
        write fails.
        """
        self.msg("writing to temporary file")
        outstream = tempfile.TemporaryFile()
        try:
            try:
                data.write(outstream)
            except Exception:
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
            except Exception:
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
        except: # not just Exception, also CTRL-C
            self.msg("write failed!!! attempting to restore original file...")
            stream.seek(0)
            stream.write(backup)
            stream.truncate()
            raise
        stream.truncate()

    def writepatch(self, stream, data):
        """Creates a binary patch for the updated file."""
        diffcmd = self.options.get('diffcmd')
        if not diffcmd:
            raise ValueError("must specify a diff command")

        # create a temporary file that won't get deleted when closed
        newfile = tempfile.NamedTemporaryFile()
        newfilename = newfile.name
        newfile.close()
        newfile = open(newfilename, "w+b")
        self.msg("writing to temporary file")
        try:
            data.write(newfile)
        except: # not just Exception, also CTRL-C
            self.msg("write failed!!!")
            raise
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
        
