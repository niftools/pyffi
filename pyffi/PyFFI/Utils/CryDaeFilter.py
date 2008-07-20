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
import os.path # basename, splitext
import textwrap # fill

import PyFFI # for PyFFI.__version__

class CryDaeError(StandardError):
    """The XML handler will throw this exception if something goes wrong while
    parsing or writing."""
    pass

def translatename(name):
    """Translate id into valid name."""
    translation = ""
    for char in name:
        if (not char.isalnum()) and char != "_":
            char = "_"
        translation += char
    return translation

class CryDaeInspector(xml.sax.handler.ContentHandler):
    """Parses dae file and gets useful information that we need when
    converting the file with CryDaeFilter."""

    def __init__(self, basename=None, matlibraryname=None):
        """Initialize the parser.

        @param basename: Base name of the CgfExportNode (this will become the
            cgf file base name).
        @type basename: str
        @param matlibraryname: Base name of the material library (this will
            become the mtl file base name).
        @type matlibraryname: str
        """
        # keep track of materials
        self.num_materials = 0

        if basename is None:
            basename = "untitled"
        self.basename = basename

        if matlibraryname is None:
            matlibraryname = basename
        self.matlibraryname = matlibraryname

        self.id_translations = {}

    def startElement(self, name, attrs):
        for attrname in ("id", "sid"):
            idvalue = attrs.get(attrname)
            if idvalue:
                idcryvalue = translatename(idvalue)
                if name == "material":
                    self.num_materials += 1
                    idcryvalue = ("%s-%02i-%s-phys1"
                                  % (self.matlibraryname, self.num_materials,
                                     idcryvalue))
                # store translation
                # this will be written in the CryDaeFilter
                if idvalue != idcryvalue:
                    self.id_translations[idvalue] = idcryvalue
        # resource compiler does not properly supports the "symbol" attribute
        # it must coincide with the target name; workaround is to make the
        # symbol name translate into the target name
        if (name == "instance_material"
            and attrs.get("symbol") and attrs.get("target")
            and attrs.get("symbol") != attrs.get("target", "#")[1:]):
            self.id_translations[attrs.get("symbol")] = self.id_translations[attrs.get("target")[1:]]

class CryDaeFilter(xml.sax.saxutils.XMLFilterBase):
    """This class contains all functions for parsing the collada xml file
    and filtering the data so it is acceptable for the Crytek resource
    compiler."""

    def __init__(self, parent, verbose=0, inspector=None):
        """Initialize the filter.

        @param parent: The parent XMLReader instance.
        @type parent: XMLReader
        @param verbose: Level of verbosity.
        @type verbose: int
        @param inspector: XML handler which inspected the file before.
        @type inspector: L{CryDaeInspector}
        """
        # call base constructor
        xml.sax.saxutils.XMLFilterBase.__init__(self, parent)
        # set some parameters
        self.verbose = verbose
        self.scenenum = 0
        self.stack = []
        self.inspector = inspector

    def startElement(self, name, attrs):
        # update element stack
        self.stack.append(name)
        # make attrs editable
        attrs = dict(attrs.items())
        # translate ids
        for attrname in ("id", "name", "symbol", "material", "sid", "texture"):
            idtranslation = self.inspector.id_translations.get(
                attrs.get(attrname))
            if idtranslation:
                if self.verbose:
                    print("translating %s %s into %s" % (attrname,
                                                         attrs[attrname],
                                                         idtranslation))
                attrs[attrname] = idtranslation
        for attrname in ("url", "source", "target"):
            urltranslation = self.inspector.id_translations.get(
                attrs.get(attrname, "#")[1:])
            if urltranslation:
                if self.verbose:
                    print("translating %s %s into %s" % (attrname,
                                                          attrs[attrname],
                                                          "#" + urltranslation))
                attrs[attrname] = "#" + urltranslation
        # technique sid=blender -> sid=default
        if name == "technique":
            if attrs.get("sid") == "blender":
                if self.verbose:
                    print("technique sid=blender converted to sid=default")
                attrs["sid"] = "default"
        # uv naming fix
        if name == "param" and attrs.get("type") == "float":
            if attrs.get("name") == "S":
                if self.verbose:
                    print("param type=float name=S converted to name=U")
                attrs["name"] = "U"
            if attrs.get("name") == "T":
                if self.verbose:
                    print("param type=float name=T converted to name=V")
                attrs["name"] = "V"
        # phong shader sid fix
        if (name in ("color", "float")
            and len(self.stack) > 3
            and self.stack[-3] in ("phong", "lambert")
            and attrs.get("sid") is None):
            if self.verbose:
                print("setting %s %s color sid"
                      % (self.stack[-3], self.stack[-2]))
            attrs["sid"] = self.stack[-2]
        # call base startElement (this will write out the element)
        xml.sax.saxutils.XMLFilterBase.startElement(self, name, attrs)
        # insert extra visual scene CryExportNode
        if name == "visual_scene":
            # insert a node
            if self.scenenum == 0:
                scenename = self.inspector.basename
            else:
                scenename = "%s%02i" % (self.inspector.basename, self.scenenum)
            cryexportnodeid = ("CryExportNode_%s-CGF-%s-DoExport-MergeNodes"
                               % (scenename, scenename))
            if self.verbose:
                print("visual scene %s:" % scenename)
                print("  inserting %s" % cryexportnodeid)
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
            # windows seperators -> platform independent seperators
            if "\\" in chars:
                print("forcing separators to '/' in texture path %s" % chars)
                chars = chars.replace("\\", "/")
            if not chars.startswith("file://"):
                if self.verbose:
                    print("adding file:// to texture path %s" % chars)
                chars = "file://" + chars
            idx = chars.lower().find("/game/")
            if idx == -1:
                if self.verbose:
                    print("""\
WARNING:
  for Crysis, your texture files should reside in
  ...\\Game\\...
  (for example: ...\\Crysis\\Mods\\MyModName\\Game\\Textures\\...\\...)
  but %s
  does not satisfy this requirement.""" % chars)
        else:
            # translate names in characters
            # (sometimes found in init_from and source elements)
            charstranslate = self.inspector.id_translations.get(chars)
            if charstranslate:
                if self.verbose:
                    print("translating characters %s into %s"
                          % (chars, charstranslate))
                chars = charstranslate

        # wrap long lines for improved readability
        #if len(chars) > 79:
        #    chars = textwrap.fill(chars, 79, break_long_words=False)
        #if len(chars) > 79:
        #    print("num elements %i" % len(chars.split()))
        #    print(chars.split())

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

def convert(infile, outfile, verbose=0, basename=None, matlibraryname=None):
    """Convert dae file using the CryDaeFilter.

    @param infile: The input file.
    @type infile: file
    @param outfile: The output file.
    @type outfile: file
    """
    if basename is None:
        basename = os.path.splitext(os.path.basename(infile.name))[0]

    if matlibraryname is None:
        matlibraryname = basename

    infile.seek(0)
    inspector = CryDaeInspector(basename=basename,
                                matlibraryname=matlibraryname)
    parser = xml.sax.make_parser()
    parser.setContentHandler(inspector)
    parser.parse(infile)

    infile.seek(0)
    parser = CryDaeFilter(xml.sax.make_parser(),
                          verbose=verbose,
                          inspector=inspector)
    parser.setContentHandler(xml.sax.saxutils.XMLGenerator(outfile))
    parser.parse(infile)

