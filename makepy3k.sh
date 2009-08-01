#!/bin/sh

git clean -x -d -f
mkdir -p py3k
cp -r pyffi scripts tests rundoctest.py py3k
2to3 -w py3k/pyffi py3k/rundoctest.py
# better, if Python 3.x is available:
#cd py3k
#../../Python-3.0.1/python ../../Python-3.0.1/Tools/scripts/2to3 -w -n pyffi rundoctest.py
#../../Python-3.0.1/python rundoctest.py

