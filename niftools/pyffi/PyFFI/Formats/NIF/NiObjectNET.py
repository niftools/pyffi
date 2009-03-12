"""Custom functions for NiObjectNET."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2009, NIF File Format Library and Tools.
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
# ***** END LICENSE BLOCK *****

def addExtraData(self, extrablock):
    """Add block to extra data list and extra data chain. It is good practice
    to ensure that the extra data has empty nextExtraData field when adding it
    to avoid loops in the hierarchy."""
    # add to the list
    num_extra = self.numExtraDataList
    self.numExtraDataList = num_extra + 1
    self.extraDataList.updateSize()
    self.extraDataList[num_extra] = extrablock
    # add to the chain
    if not self.extraData:
        self.extraData = extrablock
    else:
        lastextra = self.extraData
        while lastextra.nextExtraData:
            lastextra = lastextra.nextExtraData
        lastextra.nextExtraData = extrablock

def removeExtraData(self, extrablock):
    """Remove block from extra data list and extra data chain.

    >>> from PyFFI.Formats.NIF import NifFormat
    >>> block = NifFormat.NiNode()
    >>> block.numExtraDataList = 3
    >>> block.extraDataList.updateSize()
    >>> extrablock = NifFormat.NiStringExtraData()
    >>> block.extraDataList[1] = extrablock
    >>> block.removeExtraData(extrablock)
    >>> [extra for extra in block.extraDataList]
    [None, None]
    """
    # remove from list
    new_extra_list = []
    for extraother in self.extraDataList:
        if not extraother is extrablock:
            new_extra_list.append(extraother)
    self.numExtraDataList = len(new_extra_list)
    self.extraDataList.updateSize()
    for i, extraother in enumerate(new_extra_list):
        self.extraDataList[i] = extraother
    # remove from chain
    if self.extraData is extrablock:
        self.extraData = extrablock.nextExtraData
    lastextra = self.extraData
    while lastextra:
        if lastextra.nextExtraData is extrablock:
            lastextra.nextExtraData = lastextra.nextExtraData.nextExtraData
        lastextra = lastextra.nextExtraData

def getExtraDatas(self):
    """Get a list of all extra data blocks."""
    xtras = [xtra for xtra in self.extraDataList]
    xtra = self.extraData
    while xtra:
        if not xtra in self.extraDataList:
            xtras.append(xtra)
        xtra = xtra.nextExtraData
    return xtras

def setExtraDatas(self, extralist):
    """Set all extra data blocks from given list (erases existing data).

    >>> from PyFFI.Formats.NIF import NifFormat
    >>> node = NifFormat.NiNode()
    >>> extra1 = NifFormat.NiExtraData()
    >>> extra1.name = "hello"
    >>> extra2 = NifFormat.NiExtraData()
    >>> extra2.name = "world"
    >>> node.getExtraDatas()
    []
    >>> node.setExtraDatas([extra1, extra2])
    >>> [extra.name for extra in node.getExtraDatas()]
    ['hello', 'world']
    >>> [extra.name for extra in node.extraDataList]
    ['hello', 'world']
    >>> node.extraData is extra1
    True
    >>> extra1.nextExtraData is extra2
    True
    >>> extra2.nextExtraData is None
    True
    >>> node.setExtraDatas([])
    >>> node.getExtraDatas()
    []
    >>> # now set them the other way around
    >>> node.setExtraDatas([extra2, extra1])
    >>> [extra.name for extra in node.getExtraDatas()]
    ['world', 'hello']
    >>> [extra.name for extra in node.extraDataList]
    ['world', 'hello']
    >>> node.extraData is extra2
    True
    >>> extra2.nextExtraData is extra1
    True
    >>> extra1.nextExtraData is None
    True

    @param extralist: List of extra data blocks to add.
    @type extralist: C{list} of L{NifFormat.NiExtraData}
    """
    # set up extra data list
    self.numExtraDataList = len(extralist)
    self.extraDataList.updateSize()
    for i, extra in enumerate(extralist):
        self.extraDataList[i] = extra
    # set up extra data chain
    # first, kill the current chain
    self.extraData = None
    # now reconstruct it
    if extralist:
        self.extraData = extralist[0]
        lastextra = self.extraData
        for extra in extralist[1:]:
            lastextra.nextExtraData = extra
            lastextra = extra
        lastextra.nextExtraData = None

def addController(self, ctrlblock):
    """Add block to controller chain and set target of controller to self."""
    if not self.controller:
        self.controller = ctrlblock
    else:
        lastctrl = self.controller
        while lastctrl.nextController:
            lastctrl = lastctrl.nextController
        lastctrl.nextController = ctrlblock
    # set the target of the controller
    ctrlblock.target = self

def getControllers(self):
    """Get a list of all controllers."""
    ctrls = []
    ctrl = self.controller
    while ctrl:
        ctrls.append(ctrl)
        ctrl = ctrl.nextController
    return ctrls

def addIntegerExtraData(self, name, value):
    """Add a particular extra integer data block."""
    extra = self.cls.NiIntegerExtraData()
    extra.name = name
    extra.integerData = value
    self.addExtraData(extra)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
