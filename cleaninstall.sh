#!/bin/sh
git clean -f -d -x
python setup.py -q build
su -c 'rm -rf /usr/lib/python2.7/site-packages/PyFFI*; rm -rf /usr/lib64/python2.7/site-packages/PyFFI*; rm -rf /usr/lib/python2.7/site-packages/pyffi*; rm -rf /usr/lib64/python2.7/site-packages/pyffi*; python setup.py -q install'
rm -rf build

