"""Class definition for the main QSkope window."""

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

from PyQt4 import QtGui

from qskopelib.GlobalModel import GlobalModel
from qskopelib.DetailModel import DetailModel

from PyFFI.NIF import NifFormat
from PyFFI.CGF import CgfFormat

from types import NoneType

class QSkope(QtGui.QMainWindow):
    """Main QSkope window."""
    def __init__(self, parent = None):
        """Initialize the main window."""
        QtGui.QMainWindow.__init__(self, parent)

        # set up the menu bar
        self.createActions()
        self.createMenus()

        # set up the tree model view
        self.globalWidget = QtGui.QTreeView()
        self.globalWidget.setAlternatingRowColors(True)

        # set up the struct model view
        self.detailWidget = QtGui.QTreeView()
        self.detailWidget.setAlternatingRowColors(True)

        # set up central widget which contains everything else
        # horizontal split: left = tree view, right = struct view
        self.mainWidget = QtGui.QWidget()        
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(self.globalWidget)
        self.layout.addWidget(self.detailWidget)
        self.mainWidget.setLayout(self.layout)
        self.setCentralWidget(self.mainWidget)

        # activate status bar
        self.statusBar().clearMessage()

        # current file and arguments to save back to disk
        self.roots = []
        self.Format = NoneType
        self.formatArgs = ()

    def createActions(self):
        self.openAct = QtGui.QAction("&Open", self)
        self.openAct.setShortcut("Ctrl+O")
        self.saveAct = QtGui.QAction("&Save", self)
        self.saveAct.setShortcut("Ctrl+S")

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.openAct)
        fileMenu.addAction(self.saveAct)

    def openFile(self, filename = None):
        """Open a file, and set up the view."""
        # inform user about file being read
        self.statusBar().showMessage("Reading %s ..." % filename)

        # open the file and check type and version
        # then read the file
        stream = open(filename, "rb")
        version, user_version = NifFormat.getVersion(stream)
        if version >= 0:
            self.roots = NifFormat.read(stream, version, user_version)
            self.Format = NifFormat
            self.formatArgs = (version, user_version)
        else:
            filetype, fileversion, game = CgfFormat.getVersion(stream)
            if filetype >= 0:
                self.roots, versions = CgfFormat.read(stream,
                                                 fileversion = fileversion,
                                                 game = game)
                self.Format = CgfFormat
                self.formatArgs = (filetype, fileversion, game)
            else:
                raw_input('File format of %s not recognized' % filename)
                raise RuntimeError('File format of %s not recognized'
                                   % filename)

        # set up the models and update the views
        self.globalModel = GlobalModel(roots = self.roots)
        self.globalWidget.setModel(self.globalModel)
        self.detailModel = DetailModel(
            block = self.roots[0] if self.roots else None)
        self.detailWidget.setModel(self.detailModel)

        # update window title
        self.setWindowTitle("QSkope - %s" % filename)

        # clear status bar
        self.statusBar().clearMessage()

    def saveFile(self):
        """Save changes to disk."""
        pass
