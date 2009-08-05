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
python setup.py --command-packages bdist_nsi bdist_nsi --bitmap=win-install/pyffi_install_164x314.bmp --headerbitmap=win-install/pyffi_install_150x57.bmp --run2to3 --msvc2008sp1 --nshextra=win-install/pyffi.nsh --target-versions=2.5,2.6,2.7,3.0,3.1,3.2

