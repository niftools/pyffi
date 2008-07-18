"""Implements abstract editor base classes.

These abstract base classes provide an abstract layer for editing data in a
graphical user interface.
"""

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

class EditableBase(object):
    """The base class for all delegates."""
    def qEditableDisplay(self):
        return self.getValue()

class EditableSpinBox(EditableBase):
    """Abstract base class for data that can be edited with a spin box that
    contains an integer. Override qEditableMinimum and qEditableMaximum to
    set the minimum and maximum values that the spin box may contain.

    Requirement: getValue must return an integer."""
    def qEditableMinimum(self):
        return -0x80000000

    def qEditableMaximum(self):
        return 0x7fffffff

class EditableFloatSpinBox(EditableSpinBox):
    """Abstract base class for data that can be edited with a spin box that
    contains a float. Override qEditableDecimals to set the number of decimals
    in the editor display.

    Requirement: getValue must return a float."""

    def qEditableDecimals(self):
        return 5

class EditableLineEdit(EditableBase):
    """Abstract base class for data that can be edited with a single line
    editor.

    Requirement: getValue must return a string."""
    def qEditableDisplay(self):
        val = self.getValue()
        if len(val) > 32:
            return val[:29] + "..."
        else:
            return val

class EditableTextEdit(EditableLineEdit):
    """Abstract base class for data that can be edited with a multiline editor.

    Requirement: getValue must return a string."""
    pass

class EditableComboBox(EditableBase):
    """Abstract base class for data that can be edited with combo boxes.
    This can be used for for instance enum types.

    Requirement: getValue must return an integer."""

    def qEditableKeys(self):
        """List or tuple of strings, each string describing an item."""
        return []

    def qEditableValue(self, index):
        """Get the value of an enum index."""
        raise NotImplementedError

    def qEditableIndex(self):
        """Get current enum index."""
        raise NotImplementedError

class EditableBoolComboBox(EditableComboBox):
    """Abstract base class for data that can be edited with a bool combo box.

    Requirement: getValue must return a bool."""
    def qEditableKeys(self):
        return ("False", "True")

    def qEditableValue(self, index):
        if index == 0:
            return False
        elif index == 1:
            return True
        else:
            raise ValueError("no value for index %i" % index)

    def qEditableIndex(self):
        return 1 if self.getValue() else 0
