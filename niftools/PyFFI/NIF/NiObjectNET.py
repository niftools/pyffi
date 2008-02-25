"""Custom functions for NiObjectNET."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, NIF File Format Library and Tools.
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
    """Add block to extra data list and extra data chain."""
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

def getExtraDatas(self):
    """Get a list of all extra data blocks."""
    xtras = [xtra for xtra in self.extraDataList ]
    xtra = self.extraData
    while xtra:
        if not xtra in self.extraDataList:
            xtras.append(xtra)
        xtra = xtra.nextExtraData
    return xtras

def addController(self, ctrlblock):
    """Add block to controller chain."""
    if not self.controller:
        self.controller = ctrlblock
    else:
        lastctrl = self.controller
        while lastctrl.nextController:
            lastctrl = lastctrl.nextController
        lastctrl.nextController = ctrlblock

def getControllers(self):
    """Get a list of all controllers."""
    ctrls = []
    ctrl = self.controller
    while ctrl:
        ctrls.append(ctrl)
        ctrl = ctrl.nextController
    return ctrls
