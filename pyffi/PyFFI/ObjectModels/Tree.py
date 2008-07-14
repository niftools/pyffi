"""Base classes for visualizing data with QSkope in a tree view.

This interface is roughly based on the TreeItem example in the Qt docs:
http://doc.trolltech.com/4.4/itemviews-simpletreemodel.html

The interfaces defined here allow data to be organized in two views: a
global view which only shows 'top-level' objects (i.e. large file
blocks, chunks, and so on) and their structure, and a detail view
which shows the details of a top-level like object, that is, the
actual data they contain. L{TreeItem} and L{TreeBranch} implement the
detail view side of things, with L{TreeLeaf} implementing the actual
display of the data content. The L{TreeGlobalBranch} class implements
the global view, which does not show any actual data, but only
structure, hence there is no need for a special TreeGlobalLeaf class.
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
    """Base class used for the tree view. All objects which contain data
    is displayed by QSkope derive from this class (such as SimpleType and
    ComplexType). You should never have to derive from this class directly.
    Instead, use the L{TreeBranch} and L{TreeLeaf} classes.
    """

    def getTreeParent(self):
        """Return parent of this structure.

        @return: The parent.
        """
        raise NotImplementedError

    def getTreeNumChildren(self):
        """Return number of children of this item. Always zero for leafs,
        and of course positive for branches if they have children.
        Override this method.

        @return: Number of children as int.
        """
        raise NotImplementedError

class TreeBranch(TreeItem):
    """A tree item which may have children."""

    def getTreeChild(self, row):
        """Find row'th child. Override this method.

        @param row: The row number.
        @type row: int
        @return: The child.
        """
        raise NotImplementedError

    def getTreeChildRow(self, item):
        """Find the row number of the given child. Override this method.

        @param item: The child.
        @type item: any
        @return: The row, as int.
        """
        raise NotImplementedError

    def getTreeChildName(self, item):
        """Find the name of the given child. Override this method.

        @param item: The child.
        @type item: any
        @return: The name, as str.
        """
        raise NotImplementedError

class TreeGlobalBranch(TreeBranch):
    """A tree item that can appear in the global view as well."""

    def getTreeGlobalDataDisplay(self):
        """Construct a convenient name for the block itself.
        Override this methd."""
        raise NotImplementedError
        # possible implementation:
        #return self.name if hasattr(self, "name") else ""

    def getTreeGlobalParent(self):
        """Parent of an object in the global view. Override this method."""
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
        @return: The child (must be a L{TreeGlobalBranch}).
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

class TreeLeaf(TreeItem):
    """A tree item that does not have any children.

    The function L{getTreeDataDisplay} controls the display of the data. If the
    data must be editable, also derive the class from one of the delegate
    classes defined in L{PyFFI.ObjectModels.Delegate}, and make sure that the
    getValue and setValue functions are implemented.
    """

    def getTreeNumChildren(self):
        """Return number of items in this structure (i.e. always zero). Do not
        override this method, it is simply provided for convenience.

        @return: 0
        """
        return 0

    def getTreeDataDisplay(self):
        """Return an object that can be used to display the instance."""
        raise NotImplementedError
