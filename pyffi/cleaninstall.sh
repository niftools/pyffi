#!/bin/sh
find . -name "*.pyc" -not -wholename "*svn*" -exec rm -f {} \;
rm -rf MANIFEST build dist docs PyFFI-* win-install/manifest.nsh
python setup.py -q build
su -c 'rm -rf /usr/lib/python2.5/site-packages/PyFFI*; rm -rf /usr/lib64/python2.5/site-packages/PyFFI*; python setup.py -q install'
rm -rf build

