#!/bin/sh

VERSION=`python -c "import PyFFI; print PyFFI.__version__;"`

# generate documentation

rm -rfv docs
epydoc -v --output=docs --name='Python File Format Interface' --url='http://pyffi.sourceforge.net/' --navlink='&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://pyffi.sourceforge.net/">Python File Format Interface</a>&nbsp;&nbsp;&nbsp;</th><th class="navbar" align="center">&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://sourceforge.net"><img src="http://sflogo.sourceforge.net/sflogo.php?group_id=199269" width="88" height="31" border="0" alt="SourceForge.net Logo" /></a>&nbsp;&nbsp;&nbsp;' --top=PyFFI PyFFI

# create source and binary distributions

rm MANIFEST
python setup.py sdist --format=zip
python setup.py sdist --format=gztar
python setup.py bdist_wininst --install-script pyffipostinstallation.py --bitmap win-install/pyffi_install_152x261.bmp

# create file list for nsis installer from MANIFEST
python makensis.py

# create windows installer
rm -f "win-install/PyFFI-${VERSION}-windows.exe"
wine ~/.wine/drive_c/Program\ Files/NSIS/makensis.exe /v3 win-install/pyffi.nsi
