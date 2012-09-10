#!/bin/sh
git clean -f -d -x
python3 setup.py -q build
python3 setup.py -q sdist --format=zip
sudo pip-python3 uninstall PyFFI -y
sudo pip-python3 install dist/PyFFI-*.zip
rm -rf build

