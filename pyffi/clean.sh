#!/bin/sh
rm -rf build
rm -rf dist
find . -name "*.pyc" -not -wholename "*svn*" -exec rm {} \;
su -c 'rm -rf /usr/lib/python2.5/site-packages/PyFFI*; rm -rf /usr/lib64/python2.5/site-packages/PyFFI*'

