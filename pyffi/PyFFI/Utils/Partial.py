"""Module for partial classes.

Credits: This module is based on the 'partial' module written by
martin@v.loewis.de. The 'partial' module is licensed under the Academic Free
License version 3.0 (http://www.opensource.org/licenses/afl-3.0.php)
and can be found at http://pypi.python.org/pypi/partial/

To declare a class partial, inherit from PyFFI.Utils.Partial.Partial and from
the full class:

>>> from PyFFI.Utils.Partial import Partial, replace
>>> class SomeClass:
...     def original_method(self):
...         print("hello world")
>>> SomeClass().original_method()
hello world
>>> class ExtendedSomeClass(Partial, SomeClass):
...     def additional_method(self, arg):
...         print(arg)
...     # replacing an original method of SomeClass
...     @replace
...     def original_method(self):
...         print("replaced!")
>>> SomeClass().original_method()
replaced!
>>> SomeClass().additional_method("test")
test
>>> ExtendedSomeClass.__name__
'SomeClass'

After the ExtendedSomeClass class definition is executed, SomeClass
will have all the additional properties defined in ExtendedSomeClass;
the name ExtendedSomeClass is of no importance (and becomes an alias
for SomeClass).

If the original class already contains the definitions being added, an
exception is raised, unless they are decorated with @replace.

>>> from PyFFI.Utils.Partial import Partial
>>> class SomeClass:
...     def original_method(self):
...         print("hello world")
>>> class ExtendedSomeClass(Partial, SomeClass):
...     # replacing without the decorator will raise an exception!
...     def original_method(self):
...         print("replaced!") # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
TypeError: ...

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

class _MetaPartial(type):
    "Metaclass implementing the hook for partial class definitions."

    def __new__(cls, name, bases, dict):
        if not bases:
            # It is the class partial itself
            return type.__new__(cls, name, bases, dict)
        if len(bases) != 2:
            raise TypeError("A partial class definition must have only one \
base class to extend")
        base = bases[1]
        for k, v in dict.items():
            if k == '__module__':
                # Ignore implicit attribute
                continue
            if k in base.__dict__ and not hasattr(v, '__replace'):
                raise TypeError("%s already has %s" % (repr(base), k))
            base.__dict__[k] = v
        # Return the original class
        return base

class Partial:
    "Base class to declare partial classes. See module docstring for details."
    __metaclass__ = _MetaPartial

def replace(f):
    """Method decorator to indicate that a method shall replace 
    the method in the full class."""
    f.__replace = True
    return f

if __name__=='__main__':
    import doctest
    doctest.testmod()
