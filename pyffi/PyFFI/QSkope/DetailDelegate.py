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

# each delegate type corresponds to a QtGui delegate type
# (see _checkValidDelegate for more details)
from PyFFI.ObjectModels.XML.Delegate import DelegateComboBox     # -> QComboBox
from PyFFI.ObjectModels.XML.Delegate import DelegateFloatSpinBox # -> QDoubleSpinBox
from PyFFI.ObjectModels.XML.Delegate import DelegateSpinBox      # -> QSpinBox
from PyFFI.ObjectModels.XML.Delegate import DelegateTextEdit     # -> QTextEdit
from PyFFI.ObjectModels.XML.Delegate import DelegateLineEdit     # -> QLineEdit

# implementation details:
# http://doc.trolltech.com/4.3/model-view-delegate.html
# http://doc.trolltech.com/4.3/qitemdelegate.html#details
class DetailDelegate(QtGui.QItemDelegate):
    """Defines an editor for data in the detail view."""

    def _checkValidDelegate(self, data, editor):
        """This function checks that the delegate class has the correct editor.
        If data and editor do not correspond to one another, then a ValueError is
        raised.

        All functions checking for delegate base classes should respect
        the order in this function, because a class may derive from more than
        one delegate class. So this function determines which editor is
        preferred if this happens. The order is:
          - ComboBox
          - FloatSpinBox
          - SpinBox
          - TextEdit
          - LineEdit

        This function is only used for internal debugging purposes.
        """
        # the general idea is to check complex instances (that derive from
        # simpler ones) first

        # check combo box
        # (some combo types may also derive from spin box such as bools,
        # in that case prefer the combo box representation)
        if isinstance(data, DelegateComboBox):
            isvalid = isinstance(editor, QtGui.QComboBox)
        # check float spin box
        elif isinstance(data, DelegateFloatSpinBox):
            isvalid = isinstance(editor, QtGui.QDoubleSpinBox)
        # check spin box
        elif isinstance(data, DelegateSpinBox):
            isvalid = isinstance(editor, QtGui.QSpinBox)
        # check text editor
        elif isinstance(data, DelegateTextEdit):
            isvalid = isinstance(editor, QtGui.QTextEdit)
        # check line editor
        elif isinstance(data, DelegateLineEdit):
            isvalid = isinstance(editor, QtGui.QLineEdit)
        else:
            # data has no delegate class, which is classified as invalid
            isvalid = False

        # if invalid, raise ValueError
        if not isvalid:
            raise ValueError("data %s has bad editor %s"
                             % (data.__class__.__name__,
                                editor.__class__.__name__))

    def createEditor(self, parent, option, index):
        """Returns the widget used to change data."""
        # check if index is valid
        if not index.isValid():
            return None
        # get the data
        data = index.internalPointer()
        # determine editor by checking for delegate base classes
        # (see _checkValidDelegate for the correct delegate preference order)
        if isinstance(data, DelegateComboBox):
            # a general purpose combo box
            editor = QtGui.QComboBox(parent)
            for key in data.qDelegateKeys():
                editor.addItem(key)
        elif isinstance(data, DelegateFloatSpinBox):
            # a spinbox for floats
            editor = QtGui.QDoubleSpinBox(parent)
            editor.setMinimum(data.qDelegateMinimum())
            editor.setMaximum(data.qDelegateMaximum())
            editor.setDecimals(data.qDelegateDecimals())
        elif isinstance(data, DelegateSpinBox):
            # an integer spin box
            editor = QtGui.QSpinBox(parent)
            editor.setMinimum(data.qDelegateMinimum())
            # work around a qt "bug": maximum must be C type "int"
            # so cannot be larger than 0x7fffffff
            editor.setMaximum(min(data.qDelegateMaximum(), 0x7fffffff))
        elif isinstance(data, DelegateTextEdit):
            # a text editor
            editor = QtGui.QTextEdit(parent)
        elif isinstance(data, DelegateLineEdit):
            # a line editor
            editor = QtGui.QLineEdit(parent)
        else:
            return None
        # check validity
        self._checkValidDelegate(data, editor)
        # return the editor
        return editor

    def setEditorData(self, editor, index):
        """Provides the widget with data to manipulate."""
        # check if index is valid
        if not index.isValid():
            return None
        # determine the data and its value
        data = index.internalPointer()
        value = data.getValue()
        # check validity of editor
        self._checkValidDelegate(data, editor)
        # set editor data
        # (see _checkValidDelegate for the correct delegate preference order)
        if isinstance(data, DelegateComboBox):
            # a combo box: set the index
            editor.setCurrentIndex(data.qDelegateIndex())
        elif isinstance(data, DelegateSpinBox):
            # a (possibly float) spinbox: simply set the value
            editor.setValue(value)
        elif isinstance(data, DelegateLineEdit):
            # a text editor: set the text
            editor.setText(value)

    def updateEditorGeometry(self, editor, option, index):
        """Ensures that the editor is displayed correctly with respect to the
        item view."""
        editor.setGeometry(option.rect)

    def setModelData(self, editor, model, index):
        """Returns updated data to the model."""
        # check if index is valid
        if not index.isValid():
            return None
        # get the data
        data = index.internalPointer()
        # check validity of editor
        self._checkValidDelegate(data, editor)
        # set model data from editor value
        # (see _checkValidDelegate for the correct delegate preference order)
        if isinstance(data, DelegateComboBox):
            # a combo box: get the value from the current index
            value = data.qDelegateValue(editor.currentIndex())
        elif isinstance(data, DelegateSpinBox):
            # a regular (float) spin box
            value = editor.value()
        elif isinstance(data, DelegateLineEdit):
            # a text editor
            value = editor.text()
        else:
            # should not happen: no editor
            print("WARNING: cannot set model data for type %s"
                  % data.__class__.__name__)
            return
        # set the model data
        model.setData(index, QtCore.QVariant(value), QtCore.Qt.EditRole)
