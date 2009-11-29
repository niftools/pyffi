#!/usr/bin/python

"""A script for which creates a shell script which upgrades non-pep8
compliant attribute names.
"""

# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------

import os

import pyffi.formats.cgf
import pyffi.formats.dds
import pyffi.formats.kfm
import pyffi.formats.nif
import pyffi.formats.tga

from pyffi.object_models.xml.struct_ import StructBase

def make_shell_script(format_class, sh_file):
    # get set of names to convert
    names = set()
    for klass_name in dir(format_class):
        if klass_name.startswith("__"):
            # skip private stuff
            continue
        klass = getattr(format_class, klass_name)
        try:
            is_struct = issubclass(klass, StructBase)
        except TypeError:
            # klass is not a class
            continue
        if not is_struct:
            # klass is not a struct class
            continue
        for name, obj in list(klass.__dict__.iteritems()):
            if isinstance(obj, (int, long)):
                # skip constants
                continue
            if name.find("_") != -1:
                # skip pep8 style attributes
                continue
            # note: now, obj should be a property or a function
            names.add(name)

    # now convert them, longest first!! (to avoid trouble if one is
    # substring of another)
    for i, name in enumerate(sorted(names, key=len, reverse=True)):
        newname = format_class.name_attribute(name)
        if name != newname:
            sh_file.write(
                "echo %i%% - %s : %s\n"
                % (int((100 * i + 0.5) / len(names)), name, newname))
            sh_file.write(
                "find . -type f "
                "\( -name \"*.py\" -or -name \"*.txt\" \) -not -wholename \"*git*\" "
                "-exec perl -pi -w -e 's/%s/%s/g' {} \\;\n"
                % (name, newname))

# create conversion script
for format_class in (pyffi.formats.cgf.CgfFormat,
                     pyffi.formats.dds.DdsFormat,
                     pyffi.formats.kfm.KfmFormat,
                     pyffi.formats.nif.NifFormat,
                     pyffi.formats.tga.TgaFormat):
    with open(format_class.__name__.lower() + ".sh", "w") as sh_file:
        sh_file.write("#!/bin/sh\n\n")
        make_shell_script(format_class, sh_file)
        os.fchmod(sh_file.fileno(), 0755)
