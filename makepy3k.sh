#!/bin/sh

git clean -x -d -f
mkdir -p py3k
cp -r pyffi scripts tests rundoctest.py docs-sphinx py3k
cd py3k
../../Python-3.1.1/python ../../Python-3.1.1/Tools/scripts/2to3 -w -n pyffi rundoctest.py
#../../Python-3.1.1/python rundoctest.py

