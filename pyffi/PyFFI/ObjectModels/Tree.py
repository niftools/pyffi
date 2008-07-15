"""Abstract base classes for visualizing data (for example with Qt) in a
tree view.

The base classes are roughly based on the TreeItem example in the Qt docs:
http://doc.trolltech.com/4.4/itemviews-simpletreemodel.html

The classes defined here allow data to be organized in two views: a
global view which only shows 'top-level' objects (i.e. large file
blocks, chunks, and so on) and their structure, and a detail view
which shows the details of a top-level like object, that is, the
actual data they contain. L{DetailTreeItem} and L{DetailTreeBranch} implement the
detail view side of things, with L{DetailTreeLeaf} implementing the actual
display of the data content. The L{GlobalTreeBranch} class implements
the global view, which does not show any actual data, but only
structure, hence there is no need for a special TreeGlobalLeaf class.

Do not use any of the methods of these classes unless you are programming a
GUI application. In particular, for manipulating the data from within Python
(e.g. in spells), you should not use them, because there are more convenient
ways to access the data from within Python directly.

Note that all classes are purely abstract, because they are not intended
for code reuse, rather, they are intended to define a uniform interface
between a GUI application and the underlying data. So you can use these
safely along with other purely abstract base classes in a multiple
inheritance scheme.

@todo: Still a work in progress, classes are not actually used
anywhere yet, and names may still change.
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

class DetailTreeItem(object):
    """Base class used for the tree detail view. All objects whose data
    is displayed by QSkope derive from this class (such as SimpleType and
    ComplexType). You should never have to derive from this class directly.
    Instead, use the L{DetailTreeBranch}, L{DetailTreeLeaf}, and L{GlobalTreeBranch}
    classes.
    """

    def getDetailTreeParent(self):
        """Return parent of this structure. Override this method.

        @return: The parent, which should be a L{DetailTreeBranch} instance, or
            L{None} if this is a L{GlobalTreeBranch} (in that case the
            parent can be browsed in the global view via
            L{GlobalTreeBranch.getTreeGlobalParent}).
        """
        raise NotImplementedError

class DetailTreeBranch(DetailTreeItem):
    """A tree item which may have children."""

    def getDetailTreeNumChildren(self):
        """Return number of children of this branch.
        Override this method.

        @return: Number of children as int.
        """
        raise NotImplementedError

    def getDetailTreeChild(self, row):
        """Find row'th child. Override this method.

        @param row: The row number.
        @type row: int
        @return: The child.
        """
        raise NotImplementedError

    def getDetailTreeChildRow(self, item):
        """Find the row number of the given child. Override this method.

        @param item: The child.
        @type item: any
        @return: The row, as int.
        """
        raise NotImplementedError

    def getDetailTreeChildName(self, item):
        """Find the name of the given child. Override this method.

        @param item: The child.
        @type item: any
        @return: The name, as str.
        """
        raise NotImplementedError

class GlobalTreeBranch(DetailTreeBranch):
    """A tree branch that can appear summarized as an item in the global view,
    and also fully in the detail view."""

    def getDetailTreeParent(self):
        """Usually you would implement this to return C{None}, because
        branches which can appear in the global view have no parents in the
        detail view. Override this method.

        @return: Usually C{None}.
        """ 
        raise NotImplementedError

    def getTreeGlobalType(self):
        """The type of this global branch for display purposes.
        Override this method.

        @return: A string.
        """
        raise NotImplementedError
        # possible implementation:
        #return self.__class__.__name__

    def getTreeGlobalId(self):
        """Unique reference id for this global branch for display
        purposes. Override this method.

        @return: An integer.
        """
        raise NotImplementedError

    def getTreeGlobalDataDisplay(self):
        """Very short summary of the data of this global branch for display
        purposes. Override this method.

        @return: A string.
        """
        raise NotImplementedError
        # possible implementation:
        #return self.name if hasattr(self, "name") else ""

    def getTreeGlobalParent(self):
        """Parent of an object in the global view. Override this method.

        @return: A L{GlobalTreeBranch} instance, or C{None} for the root
            element in the global view (typically, the global view root is a
            L{PyFFI.ObjectModels.Data.Data} instance).
        """
        raise NotImplementedError

    def getTreeGlobalNumChildren(self):
        """Return number of children of this item in the global view.
        Override this method.

        @return: Number of global children as int.
        """
        raise NotImplementedError

    def getTreeGlobalChild(self, row):
        """Find row'th child for global view. Override this method.

        @param row: The row number.
        @type row: int
        @return: The child (must be a L{GlobalTreeBranch}).
        """
        raise NotImplementedError

    def getTreeGlobalChildRow(self, item):
        """Find the row number of the given child for global view.
        Override this method.

        @param item: The child.
        @type item: any
        @return: The row, as int.
        """
        raise NotImplementedError

class DetailTreeLeaf(DetailTreeItem):
    """A tree item that does not have any children.

    The function L{getTreeDataDisplay} controls the display of the data. If the
    data must be editable, also derive the class from one of the delegate
    classes defined in L{PyFFI.ObjectModels.Delegate}, and make sure that the
    getValue and setValue functions are implemented.
    """

    def getTreeDataDisplay(self):
        """Return an object that can be used to display the instance.
        Override this method.

        @return: A string.
        """
        raise NotImplementedError

