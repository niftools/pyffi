"""Signal/slot implementation for class method callbacks.

Based on an implementation by Thiago Marcos P. Santos
(see http://code.activestate.com/recipes/576477/)

Example
=======

>>> class Model(object):
...     def __init__(self, value):
...         self.__value = value
...         self.changed = Signal()
...     def set_value(self, value):
...         self.__value = value
...         self.changed() # Emit signal
...     def get_value(self):
...         return self.__value
>>> class View(object):
...     def __init__(self, model):
...         self.model = model
...         model.changed.connect(self.model_changed)
...     def model_changed(self):
...         print("New value: %i" % self.model.get_value())
>>> model = Model(10)
>>> view1 = View(model)
>>> view2 = View(model)
>>> view3 = View(model)
>>> model.set_value(20)
New value: 20
New value: 20
New value: 20
>>> del view1
>>> model.set_value(30)
New value: 30
New value: 30
>>> model.changed.clear()
>>> model.set_value(40)
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

from weakref import WeakValueDictionary

class Signal(object):
    def __init__(self):
        self.__slots = WeakValueDictionary()

    def __call__(self, *args, **kargs):
        for key, slot_im_self in self.__slots.iteritems():
            slot_im_func, slot_im_self_id = key
            slot_im_func(slot_im_self, *args, **kargs)

    def connect(self, slot):
        key = (slot.im_func, id(slot.im_self))
        self.__slots[key] = slot.im_self

    def disconnect(self, slot):
        key = (slot.im_func, id(slot.im_self))
        if key in self.__slots:
            self.__slots.pop(key)

    def clear(self):
        self.__slots.clear()

if __name__=='__main__':
    import doctest
    doctest.testmod()
