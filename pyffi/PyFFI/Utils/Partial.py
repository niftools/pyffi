"""Module for partial classes.

Credits: This module is based on the 'partial' module written by
martin@v.loewis.de. The 'partial' module is licensed under the Academic Free
License version 3.0 (http://www.opensource.org/licenses/afl-3.0.php)
and can be found at http://pypi.python.org/pypi/partial/

To extend an existing class (typically, imported from another file) using
another class, inherit from the full class and use the MetaPartial metaclass:

>>> class SomeClass(object):
...     def original_method(self):
...         print("hello world")
>>> SomeClass().original_method()
hello world
>>> class ExtendedSomeClass(SomeClass):
...     __metaclass__ = MetaPartial
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
warning is raised, unless they are decorated with @replace.

>>> import warnings
>>> warnings.simplefilter("error") # turn warnings into errors
>>> class SomeClass(object):
...     def original_method(self):
...         print("hello world")
>>> class ExtendedSomeClass(SomeClass):
...     __metaclass__ = MetaPartial
...     # replacing without the decorator will raise an exception!
...     def original_method(self):
...         print("replaced!") # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
RuntimeWarning: ...
>>> warnings.resetwarnings() # warnings no longer errors

"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, Python File Format Interface
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

import warnings

class MetaPartial(type):
    "Metaclass implementing the hook for partial class definitions."

    def __new__(cls, name, bases, dict):
        if len(bases) != 1:
            raise TypeError("A partial class definition must have only one \
base class to extend")
        base = bases[0]
        for k, v in dict.items():
            if k in ('__module__', '__metaclass__'):
                # ignore implicit attribute, and ignore
                # the MetaPartial __metaclass__ attribute
                continue
            if k in base.__dict__ and not hasattr(v, '__replace'):
                #raise TypeError("%s already has %s" % (repr(base), k))
                warnings.warn("%s already has %s" % (repr(base), k),
                              RuntimeWarning)
            setattr(base, k, v)
        # the next command would create the actual class as defined
        # (note possible metaclass conflict!!!)
        #return type.__new__(cls, name, bases, dict)
        # but we do not actually create it, let it simply be an alias of the
        # original class
        return base

def replace(f):
    """Method decorator to indicate that a method shall replace 
    the method in the full class."""
    f.__replace = True
    return f

if __name__=='__main__':
    import doctest
    doctest.testmod()

