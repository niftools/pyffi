"""Class definition for the main QSkope window."""

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

from PyQt4 import QtGui, QtCore

import PyFFI.QSkope.GlobalModel
import PyFFI.QSkope.DetailModel
import PyFFI.QSkope.DetailDelegate

import PyFFI
from PyFFI.Formats.NIF import NifFormat
from PyFFI.Formats.CGF import CgfFormat
from PyFFI.Formats.KFM import KfmFormat
from PyFFI.Formats.DDS import DdsFormat
from PyFFI.Formats.TGA import TgaFormat

from PyFFI.ObjectModels.FileFormat import FileFormat

from types import NoneType

# implementation details:
# http://doc.trolltech.com/4.3/qmainwindow.html#details
class QSkope(QtGui.QMainWindow):
    """Main QSkope window."""
    def __init__(self, parent = None):
        """Initialize the main window."""
        QtGui.QMainWindow.__init__(self, parent)

        # set up the menu bar
        self.createActions()
        self.createMenus()

        # set up the global model view
        self.globalWidget = QtGui.QTreeView()
        self.globalWidget.setAlternatingRowColors(True)

        # set up the detail model view
        self.detailWidget = QtGui.QTreeView()
        self.detailDelegate = PyFFI.QSkope.DetailDelegate.DetailDelegate()
        self.detailWidget.setItemDelegate(self.detailDelegate)
        self.detailWidget.setAlternatingRowColors(True)

        # connect global with detail:
        # if object is selected in global view, then show its details in the
        # detail view
        QtCore.QObject.connect(self.globalWidget,
                               QtCore.SIGNAL("clicked(const QModelIndex &)"),
                               self.setDetailModel)

        # set up the central widget
        self.splitter = QtGui.QSplitter()
        self.splitter.addWidget(self.globalWidget)
        self.splitter.addWidget(self.detailWidget)
        self.setCentralWidget(self.splitter)

        # activate status bar
        self.statusBar().clearMessage()

        # window title
        self.setWindowTitle("QSkope")

        # set the main application data
        self.data = None

        # restore geometry
        settings = self.getSettings(versioned = True)
        self.restoreGeometry(
            settings.value("MainWindow/geometry").toByteArray())

    def createActions(self):
        """Create the menu actions."""
        # open a file
        self.openAct = QtGui.QAction("&Open", self)
        self.openAct.setShortcut("Ctrl+O")
        QtCore.QObject.connect(self.openAct,
                               QtCore.SIGNAL("triggered()"),
                               self.openAction)

        # save a file
        self.saveAct = QtGui.QAction("&Save", self)
        self.saveAct.setShortcut("Ctrl+S")
        QtCore.QObject.connect(self.saveAct,
                               QtCore.SIGNAL("triggered()"),
                               self.saveAction)

        # save a file as ...
        self.saveAsAct = QtGui.QAction("Save As...", self)
        self.saveAsAct.setShortcut("Ctrl+Shift+S")
        QtCore.QObject.connect(self.saveAsAct,
                               QtCore.SIGNAL("triggered()"),
                               self.saveAsAction)

        # exit
        self.exitAct = QtGui.QAction("E&xit", self)
        self.exitAct.setShortcut("Ctrl+Q")
        QtCore.QObject.connect(self.exitAct,
                               QtCore.SIGNAL("triggered()"),
                               QtGui.qApp.quit)

        # tell something about QSkope
        self.aboutQSkopeAct = QtGui.QAction("About QSkope", self)
        QtCore.QObject.connect(self.aboutQSkopeAct,
                               QtCore.SIGNAL("triggered()"),
                               self.aboutQSkopeAction)

        # tell something about Qt
        self.aboutQtAct = QtGui.QAction("About Qt", self)
        QtCore.QObject.connect(self.aboutQtAct,
                               QtCore.SIGNAL("triggered()"),
                               QtGui.qApp.aboutQt)

    # implementation details:
    # http://doc.trolltech.com/4.3/mainwindows-menus.html
    def createMenus(self):
        """Create the menu bar."""
        # the file menu: open, save, save as
        fileMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.openAct)
        fileMenu.addAction(self.saveAct)
        fileMenu.addAction(self.saveAsAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAct)

        # the help menu:
        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction(self.aboutQSkopeAct)
        helpMenu.addAction(self.aboutQtAct)

    def closeEvent(self, event):
        """Called when the application is closed. Saves the settings."""
        settings = self.getSettings(versioned = True)
        settings.setValue("MainWindow/geometry",
                          QtCore.QVariant(self.saveGeometry()))
        QtGui.QMainWindow.closeEvent(self, event)


    #
    # various helper functions
    #

    def openNifFile(self, stream = None):
        """Read nif file from stream. If stream does not contain a nif file,
        then raises ValueError. Sets the self.data variable."""
        # try reading as a nif file
        data = NifFormat.Data()
        data.read(stream)
        # if succesful: parse the file and save information about it
        self.data = data

    def openCgfFile(self, stream = None):
        """Read cgf file from stream. If stream does not contain a cgf file,
        then raises ValueError. Sets the self.header, self.roots, self.footer,
        self.Format, and self.formatArgs variables."""
        # TODO: use data element

        # failed... try reading as a cgf file
        version, user_version = CgfFormat.getVersion(stream)
        # if not succesful: raise an exception
        if version < 0:
            raise ValueError("not a cgf file")
        # if succesful: parse the file and save information about it
        filetype, self.roots, versions = CgfFormat.read(
            stream, version = version, user_version = user_version)
        self.header = None
        self.footer = None
        self.Format = CgfFormat
        self.formatArgs = (version, user_version, filetype)

    def openKfmFile(self, stream = None):
        """Read kfm file from stream. If stream does not contain a kfm file,
        then raises ValueError. Sets the self.header, self.roots, self.footer,
        self.Format, and self.formatArgs variables."""
        # TODO: use data element

        # try reading as a kfm file
        version, user_version = KfmFormat.getVersion(stream)
        # if not succesful: raise an exception
        if version < 0:
            raise ValueError("not a kfm file")
        # if succesful: parse the file and save information about it
        self.header, self.roots, self.footer = KfmFormat.read(
            stream, version = version, user_version = user_version)
        self.Format = KfmFormat
        self.formatArgs = (version, user_version)

    def openDdsFile(self, stream = None):
        """Read dds file from stream. If stream does not contain a dds file,
        then raises ValueError. Sets the self.data variable.
        """
        # try reading as a nif file
        data = DdsFormat.Data()
        data.read(stream)
        # if succesful: parse the file and save information about it
        self.data = data

    def openTgaFile(self, stream = None):
        """Read tga file from stream. If stream does not contain a tga file,
        then raises ValueError. Sets the self.header, self.roots, self.footer,
        self.Format, and self.formatArgs variables."""
        # TODO: use data element

        # try reading as a tga file
        version, user_version = TgaFormat.getVersion(stream)
        # if not succesful: raise an exception
        if version < 0:
            raise ValueError("not a tga file")
        # if succesful: parse the file and save information about it
        self.header, pixeldata = TgaFormat.read(
            stream, version = version, user_version = user_version)
        self.roots = None
        self.footer = None
        self.Format = TgaFormat
        self.formatArgs = (version, user_version)

    def openFile(self, filename = None):
        """Open a file, and set up the view."""
        # inform user about file being read
        self.statusBar().showMessage("Reading %s ..." % filename)

        # open the file and check type and version
        # then read the file
        try:
            stream = open(filename, "rb")
            # try reading as a nif file
            try:
                self.openNifFile(stream)
            except ValueError:
                # failed... try reading as a cgf file
                try:
                    self.openCgfFile(stream)
                except ValueError:
                    try:
                        self.openKfmFile(stream)
                    except ValueError:
                        try:
                            self.openDdsFile(stream)
                        except ValueError:
                            try:
                                self.openTgaFile(stream)
                            except ValueError:
                                # all failed: inform user that format is not
                                # recognized
                                self.statusBar().showMessage(
                                    'File format of %s not recognized' % filename)
                                return
        except (ValueError, IOError):
            # update status bar message
            self.statusBar().showMessage("Failed reading %s (see console)"
                                         % filename)
            raise

        else:
            # update current file name
            self.fileName = filename

            # update the status bar
            self.statusBar().showMessage("Finished reading %s" % filename)

            # set up the models and update the views
            self.globalModel = PyFFI.QSkope.GlobalModel.GlobalModel(
                globalnode=self.data)
            self.globalWidget.setModel(self.globalModel)
            self.setDetailModel(
                self.globalModel.index(0, 0, QtCore.QModelIndex()))

            # update window title
            self.setWindowTitle("QSkope - %s" % self.fileName)
        finally:
            try:
                stream.close()
            except UnboundLocalError:
                pass

    def saveFile(self, filename = None):
        """Save changes to disk."""
        # TODO support dds saving as well
        if issubclass(self.Format, DdsFormat):
            self.statusBar().showMessage("Saving DDS format not supported")
            return

        # TODO support tga saving as well
        if issubclass(self.Format, TgaFormat):
            self.statusBar().showMessage("Saving TGA format not supported")
            return

        # tell user we are saving the file
        self.statusBar().showMessage("Saving %s ..." % filename)
        try:
            # open stream for writing
            stream = open(filename, "wb")
            # check type of file
            self.data.write(stream)

        except ValueError:
            # update status bar message
            self.statusBar().showMessage("Failed saving %s (see console)"
                                         % filename)
            raise
        else:
            # update status bar message
            self.statusBar().showMessage("Finished saving %s" % filename)
        finally:
            stream.close()

    @staticmethod
    def getSettings(versioned = False):
        """Return the QSkope settings."""
        if not versioned:
            return QtCore.QSettings("PyFFI", "QSkope")
        else:
            return QtCore.QSettings("PyFFI-%s" % PyFFI.__version__, "QSkope")

    #
    # slots
    #

    def setDetailModel(self, index):
        """Set the detail model given an index from the global model."""
        # if the index is valid, then get the block from its internal pointer
        # and set up the model
        if index.isValid():
            globalnode = index.internalPointer().data.node
            self.detailModel = PyFFI.QSkope.DetailModel.DetailModel(
                globalnode=globalnode,
                globalmodel=self.globalModel)
        else:
            self.detailModel = PyFFI.QSkope.DetailModel.DetailModel()
        # set the widget's model
        self.detailWidget.setModel(self.detailModel)

    def openAction(self):
        """Open a file."""
        # wrapper around openFile
        # (displays an extra file dialog)
        filename = QtGui.QFileDialog.getOpenFileName(self, "Open File")
        if filename:
            self.openFile(filename = filename)

    def saveAsAction(self):
        """Save a file."""
        # wrapper around saveAction
        # (displays an extra file dialog)
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save File")
        if filename:
            self.fileName = filename
            self.saveAction()

    def saveAction(self):
        """Save a file."""
        # wrapper around saveFile
        # (gets file name automatically from stored file name)
        if self.fileName:
            self.saveFile(filename = self.fileName)

    def aboutQSkopeAction(self):
        """Display an information window about QSkope."""
        # create the box
        mbox = QtGui.QMessageBox(self)
        # set window title and window text
        mbox.setWindowTitle("About QSkope")
        mbox.setText("""
<p>QSkope is a tool bundled with PyFFI for analyzing and editing files whose
format is supported by PyFFI. QSkope is written in Python.</p>
<p>The Python File Format Interface, or briefly PyFFI, is a general purpose
library to read and write block structured file formats.</p>
<p>For more informations visit
<a href="http://pyffi.sourceforge.net">http://pyffi.sourceforge.net</a>.</p>
<p>PyFFI is free software and comes under a BSD license. The source is
available via
<a href="http://pyffi.svn.sourceforge.net/viewvc/pyffi/trunk/">svn</a>
on <a href="http://sourceforge.net">SourceForge</a>.</p>
<p>You are running PyFFI %s.
The most recent version of PyFFI can always be downloaded from the
<a href="http://sourceforge.net/project/showfiles.php?group_id=199269">
PyFFI SourceForge Project page</a>.""" % PyFFI.__version__)
        # display the window
        mbox.exec_()
