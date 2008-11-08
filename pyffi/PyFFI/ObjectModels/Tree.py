"""Base classes for visualizing data (for example with Qt) in a
double tree view.

The base classes are roughly based on the TreeItem example in the Qt docs:
http://doc.trolltech.com/4.4/itemviews-simpletreemodel.html

The classes defined here allow data to be organized in two views: a
global view which only shows 'top-level' objects (i.e. large file
blocks, chunks, and so on) and their structure, and a detail view
which shows the details of a top-level like object, that is, the
actual data they contain. L{DetailTreeLeaf} and L{DetailTreeBranch} implement
the detail view side of things. The L{GlobalTreeBranch} class implements
the global view, which does not show any actual data, but only
structure, hence there is no need for a special C{GlobalTreeLeaf} class.

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

class TreeItem(object):
    """Base class used for the detail and global trees. All objects whose data
    is displayed by QSkope derive from this class (such as L{SimpleType} and
    L{ComplexType}). You should never have to derive from this class directly.
    Instead, use the L{DetailTreeBranch}, L{DetailTreeLeaf}, and
    L{GlobalTreeBranch} classes.
    """

    def getTreeParent(self):
        """Return parent of this structure. Override this method.

        @return: The parent, which is a L{DetailTreeBranch} instance, or
            C{None}. If C{self} is a L{GlobalTreeBranch} then the parent is also
            a L{GlobalTreeBranch}, or C{None}.
        """
        raise NotImplementedError

class DetailTreeBranch(TreeItem):
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

    def getGlobalTreeType(self):
        """The type of this global branch for display purposes.
        Override this method.

        @return: A string.
        """
        raise NotImplementedError
        # possible implementation:
        #return self.__class__.__name__

    def getGlobalTreeId(self):
        """Unique reference id for this global branch for display
        purposes. Override this method.

        @return: An integer.
        """
        raise NotImplementedError

    def getGlobalTreeDataDisplay(self):
        """Very short summary of the data of this global branch for display
        purposes. Override this method.

        @return: A string.
        """
        raise NotImplementedError
        # possible implementation:
        #return self.name if hasattr(self, "name") else ""

    def getGlobalTreeChildren(self):
        """Generator which yields all children of this item in the global view.
        Override this method.

        @return: Generator for global tree children.
        """
        raise NotImplementedError

    def getGlobalTreeNumChildren(self):
        """Return number of children of this item in the global view.
        Override this method.

        @return: Number of global children as int.
        """
        raise NotImplementedError

    def getGlobalTreeChild(self, row):
        """Find row'th child for global view. Override this method.

        @param row: The row number.
        @type row: int
        @return: The child (must be a L{GlobalTreeBranch}).
        """
        raise NotImplementedError

    def getGlobalTreeChildRow(self, item):
        """Find the row number of the given child for global view.
        Override this method.

        @param item: The child.
        @type item: any
        @return: The row, as int.
        """
        raise NotImplementedError

    def replaceGlobalTreeBranch(self, oldbranch, newbranch):
        """Replace a particular branch in the tree."""
        raise NotImplementedError

    def getGlobalTree(self):
        """Iterate over self, all children, all grandchildren, and so on.
        Do not override.
        """
        yield self
        for child in self.getGlobalTreeChildren():
            for branch in child.getGlobalTree():
                yield branch

class DetailTreeLeaf(TreeItem):
    """A tree item that does not have any children.

    The function L{getDetailTreeDataDisplay} controls the display of the data. If the
    data must be editable, also derive the class from one of the delegate
    classes defined in L{PyFFI.ObjectModels.Editable}, and make sure that the
    getValue and setValue functions are implemented.
    """

    def getDetailTreeDataDisplay(self):
        """Return an object that can be used to display the instance.
        Override this method.

        @return: A string.
        """
        raise NotImplementedError

