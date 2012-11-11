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
	make html SPHINXBUILD=sphinx-build-3.2
	popd
	mv docs-sphinx/_build/html/ docs/
fi

# create source and binary distributions

rm MANIFEST
python3 setup.py -q sdist --format=zip
python3 setup.py --command-packages bdist_nsi bdist_nsi --bitmap=win-install/pyffi_install_164x314.bmp --headerbitmap=win-install/pyffi_install_150x57.bmp --msvc2008sp1 --nshextra=win-install/pyffi.nsh --target-versions=3.0,3.1,3.2,3.3 --productkey=py3k
