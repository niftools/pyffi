#!/bin/sh
git clean -f -d -x
python3 setup.py -q build
sudo 'rm -rf /usr/lib/python3.2/site-packages/PyFFI*; rm -rf /usr/lib64/python3.2/site-packages/PyFFI*; rm -rf /usr/lib/python3.2/site-packages/pyffi*; rm -rf /usr/lib64/python3.2/site-packages/pyffi*'
rm dist/*
python3 setup.py -q sdist --format=zip
sudo pip-python3 install dist/PyFFI-*.zip
rm -rf build

