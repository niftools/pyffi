#!/usr/bin/python

"""A script for installing and uninstalling PyFFI's registry keys and desktop
icons."""

# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------

def createsubkey(key, sub_key, default_type = None, default_value = None):
    """Get the registry sub_key from hkey object key. If not found then the
    sub_key is created. If default_type is not None, then the sub_key's default
    value is set."""
    try:
        # try to open the sub_key
        hkey = _winreg.OpenKey(key, sub_key, 0, _winreg.KEY_SET_VALUE)
    except EnvironmentError:
        # opening failed, so create it
        hkey = _winreg.CreateKey(key, sub_key)
    # set its default value, if applicable
    if not default_type is None:
        _winreg.SetValue(hkey, None, default_type, default_value)
    # return the key
    return hkey

def createsubkeychain(key, *args, **kwargs):
    """Create a chain of registry keys."""
    default_type = kwargs.get("default_type")
    default_value = kwargs.get("default_value")
    for sub_key in args[:-1]:
        key = createsubkey(key, sub_key)
    createsubkey(key, args[-1], default_type, default_value)

def getsubkey(key, sub_key):
    """Get the registry sub_key from hkey object key. If not found then returns
    None. If key is None then this function also returns None."""
    if key is None:
        return None
    try:
        # try to open the sub_key
        return _winreg.OpenKey(key, sub_key)
    except EnvironmentError:
        return None

try:
    import _winreg
except ImportError:
    # not on Windows: nothing to do
    pass
else:
    import sys, os.path
    # check arguments
    if len(sys.argv) < 2:
        sys.exit()
    # get paths to various programs, scripts, and shortcuts
    pythonexe = os.path.join(sys.exec_prefix, "python.exe")
    nifoptpy  = os.path.join(sys.exec_prefix, "Scripts", "nifoptimize.py")
    qskopepy  = os.path.join(sys.exec_prefix, "Scripts", "qskope.py")
    qskopelnk = os.path.join(
        get_special_folder_path("CSIDL_DESKTOPDIRECTORY"),
        "QSkope.lnk")
    # install
    if sys.argv[1] == "-install":
        # register the .nif, .nifcache, .kf, .kfa, and .kfm extensions
        createsubkey(_winreg.HKEY_CLASSES_ROOT, ".nif",
                     _winreg.REG_SZ, "NetImmerseFile")
        createsubkey(_winreg.HKEY_CLASSES_ROOT, ".nifcache",
                     _winreg.REG_SZ, "NetImmerseFile")
        createsubkey(_winreg.HKEY_CLASSES_ROOT, ".kf",
                     _winreg.REG_SZ, "NetImmerseFile")
        createsubkey(_winreg.HKEY_CLASSES_ROOT, ".kfa",
                     _winreg.REG_SZ, "NetImmerseFile")
        createsubkey(_winreg.HKEY_CLASSES_ROOT, ".kfm",
                     _winreg.REG_SZ, "NetImmerseFile")
        # register the .cgf extension
        createsubkey(_winreg.HKEY_CLASSES_ROOT, ".cgf",
                     _winreg.REG_SZ, "CrytekGeometryFile")
        # add the optimize and qskope commands to nif
        hkeynif = createsubkey(_winreg.HKEY_CLASSES_ROOT, "NetImmerseFile",
                       _winreg.REG_SZ, "NetImmerse/Gamebryo File")
        createsubkeychain(hkeynif, "shell", "Optimize with PyFFI",
                  "command",
                  default_type = _winreg.REG_SZ,
                  default_value = '"%s" "%s" --pause "%%1"'
                  % (pythonexe, nifoptpy))
        createsubkeychain(hkeynif, "shell", "Open with QSkope",
                          "command",
                          default_type = _winreg.REG_SZ,
                          default_value = '"%s" "%s" "%%1"'
                          % (pythonexe, qskopepy))
        # add the qskope commands to cgf
        hkeycgf = createsubkey(_winreg.HKEY_CLASSES_ROOT, "CrytekGeometryFile",
                               _winreg.REG_SZ, "Crytek Geometry File")
        createsubkeychain(hkeycgf, "shell", "Open with QSkope",
                          "command",
                          default_type = _winreg.REG_SZ,
                          default_value = '"%s" "%s" "%%1"'
                          % (pythonexe, qskopepy))
        # add qskope desktop shortcut
        create_shortcut('"%s"' % pythonexe,
                        "QSkope",
                        qskopelnk,
                        '"%s"' % qskopepy)
        file_created(qskopelnk)
    # uninstall
    elif sys.argv[1] == "-remove":
        # get all the nif keys (this checks whether they exist)
        hkeynif = getsubkey(_winreg.HKEY_CLASSES_ROOT, "NetImmerseFile")
        hkeyshell = getsubkey(hkeynif, "shell")
        hkeyoptimize = getsubkey(hkeyshell, "Optimize with PyFFI")
        hkeycommand = getsubkey(hkeyoptimize, "command")
        if hkeycommand:
            hkeycommand.Close()
            _winreg.DeleteKey(hkeyoptimize, "command")
            hkeyoptimize.Close()
            _winreg.DeleteKey(hkeyshell, "Optimize with PyFFI")            
        hkeyqskope = getsubkey(hkeyshell, "Open with QSkope")
        hkeycommand = getsubkey(hkeyqskope, "command")
        if hkeycommand:
            hkeycommand.Close()
            _winreg.DeleteKey(hkeyqskope, "command")
            hkeyqskope.Close()
            _winreg.DeleteKey(hkeyshell, "Open with QSkope")            
        # get all the cgf keys (this checks whether they exist)
        hkeycgf = getsubkey(_winreg.HKEY_CLASSES_ROOT, "CrytekGeometryFile")
        hkeyshell = getsubkey(hkeycgf, "shell")
        hkeyqskope = getsubkey(hkeyshell, "Open with QSkope")
        hkeycommand = getsubkey(hkeyqskope, "command")
        if hkeycommand:
            hkeycommand.Close()
            _winreg.DeleteKey(hkeyqskope, "command")
            hkeyqskope.Close()
            _winreg.DeleteKey(hkeyshell, "Open with QSkope")            
