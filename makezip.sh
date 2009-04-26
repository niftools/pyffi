#!/bin/sh

# generate documentation (from the INSTALLED version of PyFFI)

rm -rfv docs
cd docs-sphinx
epydoc -v --output=../docs --name='Python File Format Interface' --url='http://pyffi.sourceforge.net/' --navlink='&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://pyffi.sourceforge.net/">Python File Format Interface</a>&nbsp;&nbsp;&nbsp;</th><th class="navbar" align="center">&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://sourceforge.net"><img src="http://sflogo.sourceforge.net/sflogo.php?group_id=199269" width="88" height="31" border="0" alt="SourceForge.net Logo" /></a>&nbsp;&nbsp;&nbsp;' --docformat="restructuredtext" --top=PyFFI PyFFI
cd ..

# create source and binary distributions

rm MANIFEST
python setup.py -q sdist --format=zip
python setup.py -q sdist --format=bztar

# create file list for nsis installer from MANIFEST
python makensis.py

# create windows installer
wine ~/.wine/drive_c/Program\ Files/NSIS/makensis.exe /v2 win-install/pyffi.nsi

