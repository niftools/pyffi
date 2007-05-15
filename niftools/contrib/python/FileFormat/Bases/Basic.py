# --------------------------------------------------------------------------
# FileFormat.Bases.Basic
# Implements class for basic types (xml tag <basic>).
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, NIF File Format Library and Tools.
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
#    * Neither the name of the NIF File Format Library and Tools
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
# --------------------------------------------------------------------------

# This metaclass checks for the presence of an _attrs and __doc__ attribute.
# Used as metaclass of BasicBase.
class _MetaBasicBase(type):
    def __init__(cls, name, bases, dct):
        # consistency checks
        if not dct.has_key('_isTemplate'):
            raise TypeError(str(cls) + ': missing _isTemplate attribute')

class BasicBase(object):
    """Base class from which all basic types are derived.
    
    The BasicBase class implements the interface for basic types.
    All basic types have to be derived from this class, by hand.
    They must override read, write, getValue, and setValue.

    >>> class UInt(BasicBase):
    ...     _isTemplate = False
    ...     def __init__(self, template = None):
    ...         self.__value = 0
    ...     def getValue(self):
    ...         return self.__value
    ...     def setValue(self, value):
    ...         self.__value = int(value)
    >>> x = UInt()
    >>> x.setValue('123')
    >>> x.getValue()
    123

    #>>> x.value = 456
    #>>> x.value
    #456
    """
    
    __metaclass__ = _MetaBasicBase
    _isTemplate = False
    _hasLinks = False # does the type contain a Ref or a Ptr?
    _hasRefs = False # does the type contain a Ref?
    
    def __init__(self, template = None, argument = None):
        """When overriding __init__, template and argument are
        mandatory even if the type is not a template or does not take
        an argument. This makes it easier to instanciate all types in
        a uniform manner, i.e. typ(tmpl, arg).
	
        See FileFormat/Bases/Compound.py for an example."""
	raise NotImplementedError

    # string representation
    def __str__(self):
        return str(self.getValue())

    def read(self, version = -1, user_version = 0, f = None, link_stack = [], argument = None):
        raise NotImplementedError

    def write(self, version = -1, user_version = 0, f = None, block_index_dct = {}, argument = None):
        raise NotImplementedError

    def fixLinks(self, version = -1, user_version = 0, block_dct = {}, link_stack = []):
        pass
    
    def getLinks(self, version = -1, user_version = 0):
        return []
    
    def getRefs(self, version = -1, user_version = 0):
        return []
    
    def getValue(self):
        raise NotImplementedError

    def setValue(self, value):
        raise NotImplementedError

    #value = property(getValue, setValue, None, "The value.")
