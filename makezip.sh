#!/bin/sh

# clean working copy

git clean -x -d -f

# generate documentation

rm -rfv docs
if [ "$1" = "test" ]
then
	mkdir docs
	echo "PyFFI test release - documentation not included" > docs/index.html
else
	pushd docs-sphinx
	# XXX broken
	#python3 -c 'from epydoc.cli import cli; cli()' -v --output=../docs --name='Python File Format Interface' --url='http://pyffi.sourceforge.net/' --navlink='&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://pyffi.sourceforge.net/">Python File Format Interface</a>&nbsp;&nbsp;&nbsp;</th><th class="navbar" align="center">&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://sourceforge.net"><img src="http://sflogo.sourceforge.net/sflogo.php?group_id=199269" width="88" height="31" border="0" alt="SourceForge.net Logo" /></a>&nbsp;&nbsp;&nbsp;' --docformat="restructuredtext" --top=pyffi pyffi
	# XXX stub for documentation
	mkdir ../docs; touch ../docs/index.html
	popd
fi

# create source and binary distributions

rm MANIFEST
python3 setup.py -q sdist --format=zip
python3 setup.py -q sdist --format=bztar
python3 setup.py --command-packages bdist_nsi bdist_nsi --bitmap=win-install/pyffi_install_164x314.bmp --headerbitmap=win-install/pyffi_install_150x57.bmp --msvc2008sp1 --nshextra=win-install/pyffi.nsh --target-versions=3.0,3.1,3.2 --maya --blender --productkey=py3k

version=`python3 setup.py -V`
wcrev=`git log -1 --pretty=format:%h`
if [ "$1" == "test" ]
then
	extversion=$version-$2.$wcrev
else
	extversion=$version.$wcrev
fi
pushd dist
mv PyFFI-$version.zip PyFFI-$extversion.zip
mv PyFFI-$version.tar.bz2 PyFFI-$extversion.tar.bz2
mv PyFFI-$version.win32.exe PyFFI-$extversion.win32.exe
popd

