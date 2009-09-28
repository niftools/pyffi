#!/bin/sh

# clean working copy

git clean -x -d -f

# generate documentation

rm -rfv docs
cd docs-sphinx
epydoc -v --output=../docs --name='Python File Format Interface' --url='http://pyffi.sourceforge.net/' --navlink='&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://pyffi.sourceforge.net/">Python File Format Interface</a>&nbsp;&nbsp;&nbsp;</th><th class="navbar" align="center">&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://sourceforge.net"><img src="http://sflogo.sourceforge.net/sflogo.php?group_id=199269" width="88" height="31" border="0" alt="SourceForge.net Logo" /></a>&nbsp;&nbsp;&nbsp;' --docformat="restructuredtext" --top=pyffi pyffi
cd ..

# create source and binary distributions

rm MANIFEST
python setup.py -q sdist --format=zip
python setup.py -q sdist --format=bztar
python setup.py --command-packages bdist_nsi bdist_nsi --bitmap=win-install/pyffi_install_164x314.bmp --headerbitmap=win-install/pyffi_install_150x57.bmp --run2to3 --msvc2008sp1 --nshextra=win-install/pyffi.nsh --target-versions=2.5,2.6,2.7,3.0,3.1,3.2 --maya --blender

# to build with wine: add the -k flag to keep all installer files, and run:
#cd build/bdist.linux-x86_64/nsi
#rm ../../../docs/pyffi.formats.nif.NifFormat.NiDataStream?0*; rm ../../../docs/pyffi.formats.nif.NifFormat.NiDataStream?1*; rm ../../../docs/pyffi.formats.nif.NifFormat.NiDataStream?3* # wine gets confused about control characters in file names
#cat setup.nsi | sed 's/\\home\\/Z:\\home\\/g' | sed 's/\\usr\\/Z:\\usr\\/g' | wine ~/.wine/drive_c/Program\ Files/NSIS/makensis.exe -

