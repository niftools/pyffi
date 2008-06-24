VERSION=`python -c "import PyFFI; print PyFFI.__version__"`
rm -rfv docs
epydoc -v --output=docs --name='Python File Format Interface' --url='http://pyffi.sourceforge.net/' --navlink='&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://pyffi.sourceforge.net/">Python File Format Interface</a>&nbsp;&nbsp;&nbsp;</th><th class="navbar" align="center">&nbsp;&nbsp;&nbsp;<a class="navbar" target="_top" href="http://sourceforge.net"><img src="http://sflogo.sourceforge.net/sflogo.php?group_id=199269" width="88" height="31" border="0" alt="SourceForge.net Logo" /></a>&nbsp;&nbsp;&nbsp;' --top=PyFFI PyFFI qskopelib NifTester CgfTester KfmTester

#tar cfvj PyFFI-$VERSION-apidocs.tar.bz2 apidocs/ &
#zip -9 PyFFI-$VERSION-apidocs.zip apidocs/* &
#7za a -t7z -m0=lzma -mx=9 -mfb=256 -md=64m -ms=on PyFFI-$VERSION-apidocs.7z apidocs/
#cd epydoc

