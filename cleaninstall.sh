#!/bin/sh
git clean -f -d -x
python3 setup.py -q build
su -c 'rm -rf /usr/lib/python3.1/site-packages/PyFFI*; rm -rf /usr/lib64/python3.1/site-packages/PyFFI*; rm -rf /usr/lib/python3.1/site-packages/pyffi*; rm -rf /usr/lib64/python3.1/site-packages/pyffi*; python3 setup.py -q install; chmod +x /usr/lib/python3.1/site-packages/pyffi/utils/mopper.exe'
rm -rf build

