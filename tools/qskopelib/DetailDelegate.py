"""Class definition for editing the detail view."""

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

from PyQt4 import QtCore, QtGui


# implementation details:
# http://doc.trolltech.com/4.3/model-view-delegate.html
# http://doc.trolltech.com/4.3/qitemdelegate.html#details
class DetailDelegate(QtGui.QItemDelegate):
    """Defines an editor for data in the detail view."""
    def createEditor(self, parent, option, index):
        """Returns the widget used to change data."""
        # check if index is valid
        if not index.isValid():
            return None
        # determine the data type
        data = index.internalPointer()
        value = data.getValue()
        # int and long: spin box
        if isinstance(value, bool):
            # a combo box for bools
            editor = QtGui.QComboBox(parent)
            editor.addItem("False") # index 0
            editor.addItem("True")  # index 1
        elif isinstance(value, (int, long)):
            # a regular spin box
            editor = QtGui.QSpinBox(parent)
            editor.setMinimum(-0x80000000)
            editor.setMaximum(0x7fffffff)
        elif isinstance(value, basestring):
            # a text editor
            editor = QtGui.QLineEdit(parent)
        elif isinstance(value, float):
            # a spinbox for floats
            editor = QtGui.QDoubleSpinBox(parent)
            editor.setMinimum(-0x80000000)
            editor.setMaximum(0x7fffffff)
            editor.setDecimals(5)
        else:
            return None
        # return the editor
        return editor

    def setEditorData(self, editor, index):
        """Provides the widget with data to manipulate."""
        # check if index is valid
        if not index.isValid():
            return None
        # determine the data type
        data = index.internalPointer()
        value = data.getValue()
        if isinstance(editor, QtGui.QDoubleSpinBox):
            # a spinbox for floats
            editor.setValue(value)
        elif isinstance(editor, QtGui.QSpinBox):
            # a regular spin box
            editor.setValue(value)
        elif isinstance(editor, QtGui.QLineEdit):
            # a text editor
            editor.setText(value)
        elif isinstance(editor, QtGui.QComboBox):
            # a combo box for bools
            editor.setCurrentIndex(1 if value else 0)

    def updateEditorGeometry(self, editor, option, index):
        """Ensures that the editor is displayed correctly with respect to the
        item view."""
        editor.setGeometry(option.rect)

    def setModelData(self, editor, model, index):
        """Returns updated data to the model."""
        # check if index is valid
        if not index.isValid():
            return None
        # get the editor value
        if isinstance(editor, QtGui.QSpinBox):
            # a regular spin box
            value = editor.value()
        elif isinstance(editor, QtGui.QLineEdit):
            # a text editor
            value = editor.text()
        elif isinstance(editor, QtGui.QComboBox):
            # a combo box for bools
            value = bool(editor.currentIndex())
        elif isinstance(editor, QtGui.QDoubleSpinBox):
            # a spinbox for floats
            value = editor.value()
        # set the model data
        model.setData(index, QtCore.QVariant(value), QtCore.Qt.EditRole)
