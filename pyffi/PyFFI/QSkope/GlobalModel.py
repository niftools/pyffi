"""The GlobalModel module defines a model to display the structure of a file
built from StructBase instances possibly referring to one another."""

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

from PyFFI.ObjectModels.XML.Struct import StructBase

from PyQt4 import QtGui, QtCore

class StructPtr(object):
    """A weak reference to a structure, to be used as internal pointer."""
    def __init__(self, block):
        """Store the block for future reference."""
        self.ptr = block

    def getTreeNumChildren(self):
        """Break cycles: no children."""
        return 0

# implementation references:
# http://doc.trolltech.com/4.3/model-view-programming.html
# http://doc.trolltech.com/4.3/model-view-model-subclassing.html
class GlobalModel(QtCore.QAbstractItemModel):
    """General purpose model for QModelIndexed access to data loaded with
    PyFFI."""
    # column definitions
    NUM_COLUMNS = 3
    COL_TYPE   = 0
    COL_NUMBER = 2
    COL_NAME   = 1

    def __init__(self, parent = None,
                 roots = None, header = None, footer = None):
        """Initialize the model to display the given blocks."""
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.header = header
        self.footer = footer
        # this list stores the blocks in the view
        # is a list of NiObjects for the nif format, and a list of Chunks for
        # the cgf format
        if roots is None:
            roots = []
        # set up the tree (avoiding duplicate references)
        self.refNumber = {}
        self.parentDict = {}
        self.refDict = {}
        for root in roots:
            for block in root.tree():
                # create a reference list for this block
                # if it does not exist already
                if not block in self.refDict:
                    self.refDict[block] = []
                # assign the block a number
                if not block in self.refNumber:
                    blocknum = len(self.refNumber)
                    self.refNumber[block] = blocknum
                for refblock in block.getRefs():
                    # each block can have only one parent
                    if not refblock in self.parentDict:
                        self.parentDict[refblock] = block
                        self.refDict[block].append(refblock)
                for refblock in block.getLinks():
                    # check all other links
                    # already added?
                    if refblock in self.refDict[block]:
                        continue
                    # already added as StructPtr?
                    if refblock in [ blk.ptr
                                     for blk in self.refDict[block]
                                     if isinstance(blk, StructPtr) ]:
                        continue
                    # create a wrapper around the block
                    ptrblock = StructPtr(refblock)
                    # store the references
                    self.parentDict[ptrblock] = block
                    self.refDict[block].append(ptrblock)
                    # no children
                    self.refDict[ptrblock] = []
                # check if it has a getTreeGlobalParent
                blockparent = block.getTreeGlobalParent()
                if blockparent and not block in self.refDict[blockparent]:
                    self.parentDict[block] = blockparent
                    self.refDict[blockparent].append(block)
        # get list of actual roots
        self.roots = []
        # list over all blocks
        for root in self.refDict:
            # if it is already listed: skip
            if root in self.roots:
                continue
            # if it has a parent: skip
            if root in self.parentDict:
                continue
            # it must be an actual root
            self.roots.append(root)
        # sort blocks by reference number
        self.roots.sort(key = lambda block: self.refNumber[block])

    def flags(self, index):
        """Return flags for the given index: all indices are enabled and
        selectable."""
        # all items are enabled and selectable
        if not index.isValid():
            return QtCore.Qt.ItemFlags()
        if isinstance(index.internalPointer(), StructBase):
            flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        else:
            flags = QtCore.Qt.ItemIsSelectable
        return QtCore.Qt.ItemFlags(flags)

    def data(self, index, role):
        """Return the data of model index in a particular role."""
        # check if the index is valid
        # check if the role is supported
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        # get the data for display
        data = index.internalPointer()
        if isinstance(data, StructPtr):
            data = data.ptr

        # the type column
        if index.column() == self.COL_TYPE:
            return QtCore.QVariant(data.__class__.__name__)
        elif index.column() == self.COL_NAME:
            if isinstance(data, StructBase):
                return QtCore.QVariant(data.getTreeGlobalDataDisplay())
            else:
                return QtCore.QVariant()

        elif index.column() == self.COL_NUMBER:
            if not data is self.header and not data is self.footer:
                return QtCore.QVariant(self.refNumber[data])
            else:
                return QtCore.QVariant()

        # other colums: invalid
        else:
            return QtCore.QVariant()

    def headerData(self, section, orientation, role):
        """Return header data."""
        if (orientation == QtCore.Qt.Horizontal
            and role == QtCore.Qt.DisplayRole):
            if section == self.COL_TYPE:
                return QtCore.QVariant("Type")
            elif section == self.COL_NAME:
                return QtCore.QVariant("Name")
            elif section == self.COL_NUMBER:
                return QtCore.QVariant("#")
        return QtCore.QVariant()

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Calculate a row count for the given parent index."""
        if not parent.isValid():
            # top level: one row for each block
            rows = len(self.roots)
            if not self.header is None:
                rows += 1
            if not self.footer is None:
                rows += 1
            return rows
        else:
            # get the parent child count = number of references
            data = parent.internalPointer()
            if data is self.header or data is self.footer:
                return 0
            else:
                return len(self.refDict[data])

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Return column count."""
        # column count is constant everywhere
        return self.NUM_COLUMNS

    def index(self, row, column, parent):
        """Create an index to item (row, column) of object parent.
        Internal pointers consist of the BasicBase, StructBase, or Array
        instance."""
        # check if the parent is valid
        if not parent.isValid():
            # parent is not valid, so we need a top-level object
            # return the index with row'th block as internal pointer
            if not self.header is None:
                if row == 0:
                    data = self.header
                elif row <= len(self.roots):
                    data = self.roots[row - 1]
                elif row == len(self.roots) + 1 and not self.footer is None:
                    data = self.footer
                else:
                    return QtCore.QModelIndex()
            else:
                if row < len(self.roots):
                    data = self.roots[row]
                elif row == len(self.roots) and not self.footer is None:
                    data = self.footer
                else:
                    return QtCore.QModelIndex()
        else:
            # parent is valid, so we need to go get the row'th reference
            # get the parent pointer
            data = self.refDict[parent.internalPointer()][row]
        return self.createIndex(row, column, data)

    def parent(self, index):
        """Calculate parent of a given index."""
        # get parent structure
        if not index.isValid():
            return QtCore.QModelIndex()
        data = index.internalPointer()
        # if no parent, then index must be top level object
        if data in self.roots or data is self.header or data is self.footer:
            return QtCore.QModelIndex()
        # finally, if parent's parent is not None, then it must be member of
        # some deeper nested structure, so calculate the row as usual
        parentData = self.parentDict[data]
        if parentData in self.roots:
            # top level parent
            # row number is index in roots list
            if not self.header is None:
                row = self.roots.index(parentData) + 1
            else:
                row = self.roots.index(parentData)
        else:
            # we need the row number of parentData:
            # 1) get the parent of parentData
            # 2) get the list of references of the parent of parentData
            # 3) check the index number of parentData in this list of references
            row = self.refDict[self.parentDict[parentData]].index(parentData)
        # construct the index
        return self.createIndex(row, 0, parentData)

