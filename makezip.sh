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
	rm -rf docs
	pushd docs-sphinx
	make html
	popd
	mv docs-sphinx/_build/html/ docs/
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
	extversion=py3k-$version-$2.$wcrev
else
	extversion=py3k-$version.$wcrev
fi
pushd dist
mv PyFFI-$version.zip PyFFI-$extversion.zip
mv PyFFI-$version.tar.bz2 PyFFI-$extversion.tar.bz2
mv PyFFI-$version.win32.exe PyFFI-$extversion.windows.exe
popd

