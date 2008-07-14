"""The DetailModel module defines a model to display the details of
StructBase, Array, and BasicBase instances."""

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

from PyQt4 import QtCore

# implementation references:
# http://doc.trolltech.com/4.3/model-view-programming.html
# http://doc.trolltech.com/4.3/model-view-model-subclassing.html
class DetailModel(QtCore.QAbstractItemModel):
    """General purpose model for QModelIndexed access to PyFFI data structures
    such as StructBase, Array, and BasicBase instances."""
    # column definitions
    NUM_COLUMNS = 3
    COL_NAME  = 0
    COL_TYPE  = 1
    COL_VALUE = 2

    def __init__(self, parent = None, block = None, refnumber_dict = None):
        """Initialize the model to display the given block. The refnumber_dict
        dictionary is used to handle references in the block."""
        QtCore.QAbstractItemModel.__init__(self, parent)
        # this list stores the blocks in the view
        # is a list of NiObjects for the nif format, and a list of Chunks for
        # the cgf format
        self.block = block
        self.refNumber = refnumber_dict if not refnumber_dict is None else {}

    def flags(self, index):
        """Return flags for the given index: all indices are enabled and
        selectable."""
        if not index.isValid():
            return QtCore.Qt.ItemFlags()
        # all items are enabled and selectable
        flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        # determine whether item value can be set
        if index.column() == self.COL_VALUE:
            try:
                index.internalPointer().getValue()
            except AttributeError:
                pass
            except NotImplementedError:
                pass
            else:
                flags |= QtCore.Qt.ItemIsEditable
        return QtCore.Qt.ItemFlags(flags)

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
            return QtCore.QVariant(data.qParent().qName(data))

        # the type column
        elif index.column() == self.COL_TYPE:
            return QtCore.QVariant(data.__class__.__name__)

        # the value column
        elif index.column() == self.COL_VALUE:
            # get the data value
            try:
                datavalue = data.getTreeDataDisplay()
            except NotImplementedError:
                # not implemented, so there is no value
                # but there should be a string representation
                datavalue = str(data)
            except AttributeError:
                # no getValue attribute: so no value
                return QtCore.QVariant()
            try:
                # see if the data is in the blocks list
                # if so, it is a reference
                blocknum = self.refNumber[datavalue]
            except (KeyError, TypeError):
                # note: TypeError occurs if datavalue is not a hashable type
                # not a reference: return the datavalue QVariant
                valuestr = str(datavalue)
                if len(valuestr) > 128:
                    return QtCore.QVariant("...")
                return QtCore.QVariant(
                    valuestr.replace("\n", " ").replace("\r", " "))
            else:
                # handle references
                if not hasattr(datavalue, "name") or not datavalue.name:
                    return QtCore.QVariant(
                        "%i [%s]" % (blocknum, datavalue.__class__.__name__))
                else:
                    return QtCore.QVariant(
                        "%i (%s)" % (blocknum, datavalue.name))

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
            # top level: one row for each attribute
            return self.block.qChildCount()
        else:
            # get the parent child count
            return parent.internalPointer().qChildCount()

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
            # return the row'th attribute
            data = self.block.qChild(row)
        else:
            # parent is valid, so we need to go get the row'th attribute
            # get the parent pointer
            data = parent.internalPointer().qChild(row)
        return self.createIndex(row, column, data)

    def parent(self, index):
        """Calculate parent of a given index."""
        # get parent structure
        parentData = index.internalPointer().qParent()
        # if parent's parent is None, then index must be a top
        # level object, so return invalid index
        if parentData.qParent() is None:
            return QtCore.QModelIndex()
        # if parent's parent is not None, then it must be member of
        # some deeper nested structure, so calculate the row as usual
        else:
            row = parentData.qParent().qRow(parentData)
        # construct the index
        return self.createIndex(row, 0, parentData)

    def setData(self, index, value, role):
        """Set data of a given index from given QVariant value."""
        if role == QtCore.Qt.EditRole:
            # fetch the current data, as a regular Python type
            data = index.internalPointer()
            currentvalue = data.getValue()
            # transform the QVariant value into the right class
            if isinstance(currentvalue, (int, long)):
                # use long type to work around QVariant(0xffffffff).toInt() bug
                pyvalue, ok = value.toLongLong()
            elif isinstance(currentvalue, float):
                pyvalue, ok = value.toDouble()
            elif isinstance(currentvalue, basestring):
                pyvalue = str(value.toString())
                ok = True
            elif isinstance(currentvalue, bool):
                pyvalue, ok = value.toBool()
            else:
                # type not supported
                return False
            # check if conversion worked
            if not ok:
                return False
            # set the value
            data.setValue(pyvalue)
            # tell everyone that the data has changed
            self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                                    index, index)
            return True
        # all other cases: failed
        return False
