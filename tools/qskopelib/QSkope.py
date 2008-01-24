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

from PyQt4 import QtGui, QtCore

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

        # connect global with detail
        QtCore.QObject.connect(self.globalWidget,
                               QtCore.SIGNAL("clicked(const QModelIndex &)"),
                               self.setDetailModel)

        # set up the docks
        self.setCentralWidget(self.globalWidget)
        ## alternative if central widget changes in future:
        ## global block list dock
        #self.globalDock = QtGui.QDockWidget("Block List", self)
        #self.globalDock.setWidget(self.globalWidget)
        #self.globalDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        #self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.globalDock)

        # block detail dock
        self.detailDock = QtGui.QDockWidget("Block Details", self)
        self.detailDock.setWidget(self.detailWidget)
        self.detailDock.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.detailDock)

        # activate status bar
        self.statusBar().clearMessage()

        # window title
        self.setWindowTitle("QSkope")

        # current file and arguments to save back to disk
        self.roots = []
        self.Format = NoneType
        self.formatArgs = ()

    def createActions(self):
        """Create the menu actions."""
        self.openAct = QtGui.QAction("&Open", self)
        self.openAct.setShortcut("Ctrl+O")
        QtCore.QObject.connect(self.openAct,
                               QtCore.SIGNAL("triggered()"),
                               self.openAction)
        
        self.saveAct = QtGui.QAction("&Save", self)
        self.saveAct.setShortcut("Ctrl+S")

    def createMenus(self):
        """Create the menu bar."""
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.openAct)
        fileMenu.addAction(self.saveAct)

    #
    # various helper functions
    #

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
                self.statusBar().showMessage(
                    'File format of %s not recognized.' % filename)
                return

        # set up the models and update the views
        self.globalModel = GlobalModel(roots = self.roots)
        self.globalWidget.setModel(self.globalModel)
        self.setDetailModel(
            self.globalModel.index(0, 0, QtCore.QModelIndex()))

        # update window title
        self.setWindowTitle("QSkope - %s" % filename)

        # clear status bar
        self.statusBar().clearMessage()

    def saveFile(self):
        """Save changes to disk."""
        pass

    #
    # slots
    #

    def setDetailModel(self, index):
        """Set the detail model given an index from the global model."""
        if index.isValid():
            self.detailModel = DetailModel(block = index.internalPointer())
        else:
            self.detailModel = DetailModel()
        self.detailWidget.setModel(self.detailModel)

    def openAction(self):
        self.openFile(
            filename = QtGui.QFileDialog.getOpenFileName(self, "Open File"))
