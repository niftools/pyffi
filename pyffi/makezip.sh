#!/bin/sh

# generate documentation

rm -rfv docs
epydoc -v --output=docs --name='Python File Format Interface' --url='http://pyffi.sourceforge.net/' --navlink='&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://pyffi.sourceforge.net/">Python File Format Interface</a>&nbsp;&nbsp;&nbsp;</th><th class="navbar" align="center">&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://sourceforge.net"><img src="http://sflogo.sourceforge.net/sflogo.php?group_id=199269" width="88" height="31" border="0" alt="SourceForge.net Logo" /></a>&nbsp;&nbsp;&nbsp;' --top=PyFFI PyFFI

# create source and binary distributions

rm MANIFEST
python setup.py sdist --format=zip
python setup.py sdist --format=bztar
python setup.py bdist_wininst --install-script pyffipostinstallation.py --bitmap pyffi_install_152x261.bmp

