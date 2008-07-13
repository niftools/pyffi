"""Base classes for visualizing data with QSkope in a tree view.

This interface is roughly based on the TreeItem example in the Qt docs:
http://doc.trolltech.com/4.4/itemviews-simpletreemodel.html
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
    ComplexType).
    """

    def __init__(self, **kwargs):
        """Initializes the instance.

        @param parent: The parent of this instance, that is, the instance this
            instance is an attribute of.
        @type parent: C{NoneType} or L{ComplexType}
        """
        self._parent = kwargs.get(parent)

    def qParent(self):
        """Return parent of this structure.

        @return: The parent.
        """
        return self._parent

def TreeBranch(TreeItem):
    """A tree item which may have children."""

    def qChildCount(self):
        """Return number of items in this structure. Zero for simple
        types, positive for structures and arrays.

        @return: Number of children as int.
        """
        raise NotImplementedError

    def qChild(self, row):
        """Find item at given row. Override for complex types.

        @param row: The row number.
        @type row: int
        @return: The child.
        """
        raise NotImplementedError

    def qRow(self, item):
        """Find the row number of the given item. Override for complex
        types.

        @param item: The child.
        @type item: any
        @return: The row, as int.
        """
        raise NotImplementedError

    def qName(self, item):
        """Find the name of the given item. Override for complex types.

        @param item: The child.
        @type item: any
        @return: The name, as str.
        """
        raise NotImplementedError

    def qBlockName(self):
        """Construct a convenient name for the block itself."""
        return self.name if hasattr(self, "name") else ""

    # extra function for global view, override if required
    def qBlockParent(self):
        """This can be used to return a parent of an object, if the parent
        object does not happen to link to the object (for instance the
        MeshMorphTargetChunk in the cgf format is an example)."""
        return None

class TreeLeaf(TreeItem):
    """A tree item that does not have any children.

    The function L{qDataDisplay} controls the display of the data. If the
    data must be editable, also derive the class from one of the delegate
    classes defined in L{PyFFI.ObjectModels.Delegate}, and make sure that the
    getValue and setValue functions are implemented.
    """

    def qDataDisplay(self):
        """Return an object that can be used to display the instance.

        @return: str(self)
        """
        return str(self)

