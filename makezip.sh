#!/bin/sh

# clean working copy

git clean -x -d -f

# create package for blender

mkdir pyffi-blender
cp -r pyffi pyffi-blender
rm pyffi-blender/pyffi/utils/mopper.exe
rm -r pyffi-blender/pyffi/formats/cgf
rm -r pyffi-blender/pyffi/formats/dae
rm -r pyffi-blender/pyffi/formats/kfm
rm -r pyffi-blender/pyffi/formats/tga
rm -r pyffi-blender/pyffi/spells/cgf
rm -r pyffi-blender/pyffi/spells/dae
rm -r pyffi-blender/pyffi/spells/kfm.py
rm -r pyffi-blender/pyffi/spells/tga.py
rm -r pyffi-blender/pyffi/object_models/mex
rm -r pyffi-blender/pyffi/object_models/xsd
rm -r pyffi-blender/pyffi/qskope
rm -r pyffi-blender/pyffi/fileformat.dtd
cd pyffi-blender
zip -r9 ../pyffi-blender.zip pyffi
cd ..

# generate documentation (from the INSTALLED version of PyFFI)

rm -rfv docs
cd docs-sphinx
epydoc -v --output=../docs --name='Python File Format Interface' --url='http://pyffi.sourceforge.net/' --navlink='&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://pyffi.sourceforge.net/">Python File Format Interface</a>&nbsp;&nbsp;&nbsp;</th><th class="navbar" align="center">&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://sourceforge.net"><img src="http://sflogo.sourceforge.net/sflogo.php?group_id=199269" width="88" height="31" border="0" alt="SourceForge.net Logo" /></a>&nbsp;&nbsp;&nbsp;' --docformat="restructuredtext" --top=pyffi pyffi
cd ..

# create source and binary distributions

rm MANIFEST
python setup.py -q sdist --format=zip
python setup.py -q sdist --format=bztar

# create file list for nsis installer from MANIFEST
python makensis.py

# create windows installers
wine ~/.wine/drive_c/Program\ Files/NSIS/makensis.exe /v2 win-install/pyffi-py2.5.nsi
wine ~/.wine/drive_c/Program\ Files/NSIS/makensis.exe /v2 win-install/pyffi-py2.6.nsi

