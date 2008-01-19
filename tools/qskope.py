"""The qskope script visualizes the structure of PyFFI structures and arrays."""

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
# ***** END LICENCE BLOCK *****

from PyQt4 import QtGui, QtCore

from PyFFI.Bases.Basic import BasicBase
from PyFFI.Bases.Struct import StructBase
from PyFFI.Bases.Array import Array, _ListWrap

from PyFFI.NIF import NifFormat
from PyFFI.CGF import CgfFormat

# helper function to calculate index using object identity "is"
# (rather than __eq__ as used by list.index)
def getIndex(itemlist, item):
    for num, it in enumerate(list.__iter__(itemlist)):
        if it is item:
            return num
    raise ValueError("getIndex(itemlist, item): item not in itemlist")

# implementation references:
# http://doc.trolltech.com/4.3/model-view-programming.html
# http://doc.trolltech.com/4.3/model-view-model-subclassing.html
class BaseModel(QtCore.QAbstractItemModel):
    """General purpose model for access to data loaded with PyFFI."""
    # column definitions
    NUM_COLUMNS = 3
    COL_TYPE  = 0
    COL_NAME  = 1
    COL_VALUE = 2

    def __init__(self, parent = None, blocks = None):
        """Initialize the model to display the given blocks."""
        QtCore.QAbstractItemModel.__init__(self, parent)
        # this list stores the blocks in the view
        # is a list of NiObjects for the nif format, and a list of Chunks for
        # the cgf format
        self.blocks = blocks if not blocks is None else []

    def flags(self, index):
        """Return flags for the given index: all indices are enabled and
        selectable."""
        if not index.isValid():
            return 0
        return QtCore.Qt.ItemFlags(QtCore.Qt.ItemIsEnabled
                                   | QtCore.Qt.ItemIsSelectable)

    def data(self, index, role):
        """Return the data of model index in a particular role."""
        # check if the index is valid
        # check if the role is supported
        if not index.isValid() or role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        # get the data for display
        data = index.internalPointer()

        # the name column
        if index.column() == self.COL_NAME:
            # only structures have named attributes
            if isinstance(data._parent, StructBase):
                return QtCore.QVariant(
                    data._parent._names[getIndex(data._parent._items, data)])
            # for arrays use the index as name
            elif isinstance(data._parent, _ListWrap):
                return QtCore.QVariant(
                    "[%i]" % getIndex(data._parent._items, data))
            else:
                return QtCore.QVariant()

        # the type column
        elif index.column() == self.COL_TYPE:
            try:
                blocknum = getIndex(self.blocks, data)
            except ValueError:
                # not a top level object: just print their class name
                return QtCore.QVariant(data.__class__.__name__)
            else:
                # top level objects: index plus class name
                return QtCore.QVariant(
                    "[%i] %s" % (blocknum, data.__class__.__name__))

        # the value column
        elif index.column() == self.COL_VALUE and isinstance(data, BasicBase):
            # get the data value
            try:
                datavalue = data.getValue()
            except NotImplementedError:
                datavalue = str(data)
            try:
                blocknum = getIndex(self.blocks, datavalue)
            except ValueError:
                # not a reference: return the datavalue QVariant
                return QtCore.QVariant(str(datavalue))
            else:
                # handle references
                return QtCore.QVariant(
                    "[%i] %s" % (blocknum,
                                 datavalue.__class__.__name__))

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
            if section == self.COL_VALUE:
                return QtCore.QVariant("Value")
        return QtCore.QVariant()

    def rowCount(self, parent = QtCore.QModelIndex()):
        """Calculate a row count for the given parent index."""
        if not parent.isValid():
            # top level: one row for each block
            return len(self.blocks)
        else:
            # get the parent data
            parentData = parent.internalPointer()
            # struct and array: number of items
            if isinstance(parentData, (StructBase, Array, _ListWrap)):
                return len(parentData._items)
            # basic types do not expand, so rows is zero
            elif isinstance(parentData, BasicBase):
                return 0
            else:
                # should not happen, print message if it does
                raise RuntimeError("bad parent data")

    def columnCount(self, parent = QtCore.QModelIndex()):
        """Return column count."""
        # column count is constant everywhere
        return self.NUM_COLUMNS

    def index(self, row, column, parent):
        """Create an index to item (row, column) of object parent.
        Internal pointers consist of the BasicBase, StructBase, or Array
        instance."""
        # check if we have such index
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()
        # check if the parent is valid
        if not parent.isValid():
            # parent is not valid, so we need a top-level object
            # return the index with row'th block as internal pointer
            data = self.blocks[row]
        else:
            # parent is valid, so we need to go get the row'th attribute
            # get the parent pointer
            parentData = parent.internalPointer()
            if isinstance(parentData, (StructBase, Array, _ListWrap)):
                # TODO fix _ListWrap class so we can write simply
                # parentData._items[row]
                data = list.__getitem__(parentData._items, row)
            else:
                return QtCore.QModelIndex()
        index = self.createIndex(row, column, data)
        return index

    def parent(self, index):
        """Calculate parent of a given index."""
        data = index.internalPointer()
        try:
            parentData = data._parent
        except AttributeError:
            raise RuntimeError(
                "no parent attribute for data %s of class %s"
                %(data, data.__class__.__name__))
        if parentData is None:
            return QtCore.QModelIndex()
        elif parentData._parent is None:
            row = self.blocks.index(parentData)
        else:
            row = getIndex(parentData._parent._items, parentData)
        return self.createIndex(row, 0, parentData)

if __name__ == "__main__":
    import sys
    global app, model

    stream = open(sys.argv[1], "rb")
    version, user_version = NifFormat.getVersion(stream)
    if version >= 0:
        blocks = NifFormat.read(stream, version, user_version,
                                rootsonly = False)
    else:
        filetype, fileversion, game = CgfFormat.getVersion(stream)
        if filetype >= 0:
            blocks, versions = CgfFormat.read(stream,
                                              fileversion = fileversion,
                                              game = game)
        else:
            raise RuntimeError("not a recognized file format")

    app = QtGui.QApplication(sys.argv)
    view = QtGui.QTreeView()
    model = BaseModel(blocks = blocks)
    view.setModel(model)
    view.setWindowTitle("QSkope")
    view.show()
    sys.exit(app.exec_())
