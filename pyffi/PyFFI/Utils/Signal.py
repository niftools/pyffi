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
