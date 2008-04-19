"""Full implementation of base classes for basic types."""

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

# import delegate classes

from PyFFI.Bases.Delegate import DelegateSpinBox
from PyFFI.Bases.Delegate import DelegateFloatSpinBox
from PyFFI.Bases.Delegate import DelegateLineEdit
from PyFFI.Bases.Delegate import DelegateBoolComboBox

# import partial fast C implementation

from PyFFI.Bases._Basic import CBasicBase
from PyFFI.Bases._Basic import CFloatBase
from PyFFI.Bases._Basic import CIntBase, CUIntBase
from PyFFI.Bases._Basic import CShortBase, CUShortBase
from PyFFI.Bases._Basic import CByteBase, CUByteBase

# the full classes, with class variables and class methods

class BasicBase(CBasicBase):
    _isTemplate = False
    _hasLinks = False
    _hasRefs = False
    _hasStrings = False

# note: getSize static methods required for enums: those need the size of the
#       type from the class (not from an instance)

class FloatBase(CFloatBase, BasicBase, DelegateFloatSpinBox):
    @staticmethod
    def getSize(**kwargs): return 4

class IntBase(CIntBase, BasicBase, DelegateSpinBox):
    @staticmethod
    def getSize(**kwargs): return 4

class UIntBase(CUIntBase, BasicBase, DelegateSpinBox):
    @staticmethod
    def getSize(**kwargs): return 4

class ShortBase(CShortBase, BasicBase, DelegateSpinBox):
    @staticmethod
    def getSize(**kwargs): return 2

class UShortBase(CUShortBase, BasicBase, DelegateSpinBox):
    @staticmethod
    def getSize(**kwargs): return 2

class ByteBase(CByteBase, BasicBase, DelegateSpinBox):
    @staticmethod
    def getSize(**kwargs): return 1

class UByteBase(CUByteBase, BasicBase, DelegateSpinBox):
    @staticmethod
    def getSize(**kwargs): return 1
