"""Utility functions for parsing a collada file and generating a similar
collada file which can be used with Crytek's resource compiler.

The conversion is implemented as an XML filter: see the L{CryDaeFilter} class
for more details.
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

import xml.sax
import xml.sax.saxutils
import optparse
import PyFFI # for PyFFI.__version__

class CryDaeError(StandardError):
    """The XML handler will throw this exception if something goes wrong while
    parsing or writing."""
    pass

class CryDaeFilter(xml.sax.saxutils.XMLFilterBase):
    """This class contains all functions for parsing the collada xml file
    and filtering the data so it is acceptable for the Crytek resource
    compiler."""

    def __init__(self, parent, verbose=0, basename=''):
        """Initialize the filter.

        @param parent: The parent XMLReader instance.
        @type parent: XMLReader
        @param verbose: Level of verbosity.
        @type verbose: int
        @param basename: Base name of the CgfExportNode (this will become the
            cgf file base name).
        @type basename: str
        """
        # call base constructor
        xml.sax.saxutils.XMLFilterBase.__init__(self, parent)
        # set some parameters
        self.verbose = verbose
        self.basename = basename
        self.scenenum = 0
        self.stack = []

    def startElement(self, name, attrs):
        # update element stack
        self.stack.append(name)
        # call base startElement
        xml.sax.saxutils.XMLFilterBase.startElement(self, name, attrs)
        # insert extra visual scene CryExportNode
        if name == "visual_scene":
            # insert a node
            if self.basename:
                if self.scenenum == 0:
                    scenename = self.basename
                else:
                    scenename = "%s%03i" % (self.basename, self.scenenum)
            else:
                # no base name: use scene name, and fall back on 'untitled'
                scenename = attrs.get("name", "untitledscene%03i"
                                      % self.scenenum)
            cryexportnodeid = ("CryExportNode_%s-CGF-%s-DoExport-MergeNodes"
                               % (scenename, scenename))
            if self.verbose:
                print("visual scene '%s'" % scenename)
                print("  inserting '%s'" % cryexportnodeid)
            self.startElement("node", {"id": cryexportnodeid})
            self.startElement("translate", {"sid": "translation"})
            self.characters("0 0 0")
            self.endElement("translate")
            self.startElement("rotate", {"sid": "rotation_z"})
            self.characters("0 0 1 0")
            self.endElement("rotate")
            self.startElement("rotate", {"sid": "rotation_y"})
            self.characters("0 1 0 0")
            self.endElement("rotate")
            self.startElement("rotate", {"sid": "rotation_x"})
            self.characters("1 0 0 0")
            self.endElement("rotate")
            self.startElement("scale", {"sid": "scale"})
            self.characters("1 1 1")
            self.endElement("scale")
            self.scenenum += 1

    def characters(self, chars):
        if (len(self.stack) >= 2
            and self.stack[-2] == "image" and self.stack[-1] == "init_from"):
            # texture path
            idx = chars.lower().find("\\game\\")
            if idx != -1:
                # texture path relative to Game
                chars = chars[idx+6:]
                if self.verbose:
                    print("truncating texture path '%s'" % chars)
            else:
                if self.verbose:
                    print("""\
WARNING:
  for Crysis, your texture files should reside in
  ...\\Game\\...
  (for example: ...\\Crysis\\Mods\\MyModName\\Game\\Textures\\...\\...)
  but %s
  does not satisfy this requirement.""" % chars)

        # call base characters
        xml.sax.saxutils.XMLFilterBase.characters(self, chars)

    def endElement(self, name):
        # close the extra visual scene CryExportNode
        if name == "visual_scene":
            self.endElement("node")
        # update element stack
        startname = self.stack.pop()
        if name != startname:
            raise ValueError("invalid xml (%s tag closed by %s tag)"
                             % (name, startname))
        # call base endElement
        xml.sax.saxutils.XMLFilterBase.endElement(self, name)

def convert(infile, outfile, verbose=0, basename=''):
    """Convert dae file using the CryDaeFilter.

    @param infile: The input file.
    @type infile: file
    @param outfile: The output file.
    @type outfile: file
    """
    parser = CryDaeFilter(xml.sax.make_parser(),
                          verbose=verbose, basename=basename)
    parser.setContentHandler(xml.sax.saxutils.XMLGenerator(outfile))
    parser.parse(infile)

