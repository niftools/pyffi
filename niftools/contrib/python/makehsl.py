# --------------------------------------------------------------------------
# makehsl
# Make hex structure libraries for all nif versions.
# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, NIF File Format Library and Tools.
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
# ***** END LICENCE BLOCK *****
# --------------------------------------------------------------------------

import sys
from types import *

from NifFormat.NifFormat import NifFormat

def find_templates():
    # find all types that are used as a template (excluding the ones
    # occuring in Ref & its subclass Ptr)
    templates = set()
    for cls in NifFormat.xmlCompound:
        for attrname, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver in cls._attributeList:
            if tmpl != None and tmpl != NoneType and not issubclass(typ, NifFormat.Ref):
                templates.add(tmpl)
    return templates

def write_hsl(f, ver, templates):
    # map basic NifFormat types to HWS types and byte size
    # (byte size is needed for enums)
    hsl_types = {
        NifFormat.int    : ('signed   __int32', 4),
        NifFormat.uint   : ('unsigned __int32', 4),
        NifFormat.short  : ('signed   __int16', 2),
        NifFormat.ushort : ('unsigned __int16', 2),
        NifFormat.byte   : ('unsigned __int8 ', 1),
        NifFormat.char   : ('char            ', 1),
        NifFormat.float  : ('double          ', 4),
        NifFormat.Ref    : ('signed   __int32', 4),
        NifFormat.Ptr    : ('signed   __int32', 4) }

    if ver <= 0x04000002:
        hsl_types[NifFormat.bool] = ('unsigned __int32', 4)
    else:
        hsl_types[NifFormat.bool] = ('unsigned __int8 ', 1)

    # write header
    f.write("""// hex structure library for NIF Format 0x%08X
#pragma maxarray(65536); // Increase the max array length

"""%ver)

    # write each enum class
    for cls in NifFormat.xmlEnum:
        write_enum(cls, ver, hsl_types, f)

    # write each compound class
    for cls in NifFormat.xmlCompound:
        if cls.__name__[:3] == 'ns ': continue # cheat: skip ns types
        if not cls._isTemplate:
            # write regular class
            write_struct(cls, ver, hsl_types, f, None)
        else:
            # write template classes
            for template in templates:
                write_struct(cls, ver, hsl_types, f, template)

def write_enum(cls, ver, hsl_types, f):
    # set enum size
    f.write('#pragma enumsize(%s)\n'%hsl_types[cls.__bases__[0]][1])
    f.write('enum ' + cls.__name__ + ' {\n')
    # list of all non-private attributes gives enum constants
    enum_items = [x for x in cls.__dict__.items() if x[0][:2] != '__']
    # sort them by value
    enum_items = sorted(enum_items, key=lambda x: x[1])
    # and write out all name, value pairs
    for const_name, const_value in enum_items[:-1]:
        f.write('  ' + const_name + ' = ' + str(const_value) + ',\n')
    const_name, const_value = enum_items[-1]
    f.write('  ' + const_name + ' = ' + str(const_value) + '\n')
    f.write('};\n\n')

def write_struct(cls, ver, hsl_types, f, template):
    # open the structure
    if not template:
        f.write('struct ' + cls.__name__ + ' {\n')
    else:
        f.write('struct ' + cls.__name__ + '_' + template.__name__ + ' {\n')
    for attrname, typ, default, tmpl, arg, arr1, arr2, cond, ver1, ver2, userver in cls._attributeList:
        # is the attribute present in this version?
        if ver1 and ver1 > ver: continue
        if ver2 and ver2 < ver: continue
        s = '  '
        # get the attribute type name
        if typ == NoneType: typ = template
        try:
            s += hsl_types[typ][0]
        except KeyError:
                s += typ.__name__
        # get the attribute template type name
        if tmpl != None and not issubclass(typ, NifFormat.Ref):
            if tmpl == NoneType: tmpl = template
            s += '_'
            s += tmpl.__name__ # note: basic types are named by their xml name in the template
        # attribute name
        s = s.ljust(20) + ' ' + attrname
        # array arguments
        if arr1 != None:
            if arr2 == None:
                s += '[' + str(arr1._left) + ']'
                if arr1._op:
                    s += ' // WARNING - should be [' + str(arr1) + ']'
            else:
                s += '[' + str(arr1._left) + ' * ' + str(arr2._left) + ']'
                if arr1._op or arr2._op:
                    s += ' // WARNING - should be [' + str(arr1) + ' * ' + str(arr2) + ']'
        f.write(s + ';\n')
    # close the structure
    f.write('};\n\n')

if __name__ == '__main__':
    # list all types used as a template
    templates = find_templates()
    # write out hex structure library for each nif version
    for ver_str, ver in NifFormat.versions.items():
        f = open('nif_' + ver_str.replace('.', '_') + '.hsl', 'w')
        try:
            write_hsl(f, ver, templates)
        finally:
            f.close()
