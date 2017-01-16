@echo off

rem clean working copy

git clean -x -d -f

rem generate documentation

del docs\*.*
rem cd docs-sphinx
rem %PYTHONPATH%\python.exe %PYTHONPATH%\Scripts\epydoc.py  -v --output=..\docs --name="Python File Format Interface" --url="https://github.com/niftools/pyffi" --navlink="&nbsp;&nbsp;&nbsp;<a class=\"navbar\" target=\"_top\" href=\"https://github.com/niftools/pyffi\">Python File Format Interface</a>&nbsp;&nbsp;&nbsp;</th><th class=\"navbar\" align=\"center\">&nbsp;&nbsp;&nbsp;" --docformat="restructuredtext" --top=pyffi pyffi
rem cd ..
mkdir docs
echo "PyFFI test release - documentation not included" > docs\index.html

rem create source and binary distributions

del MANIFEST
python setup.py -q sdist --format=zip
python setup.py --command-packages bdist_nsi bdist_nsi --bitmap=win-install/pyffi_install_164x314.bmp --headerbitmap=win-install/pyffi_install_150x57.bmp --msvc2008sp1 --nshextra=win-install/pyffi.nsh --target-versions=3.0,3.1,3.2,3.3 --productkey=py3k --nsis="%NSISHOME%"
