#!/bin/sh

rm -rf py3k
mkdir -p py3k
cp -r pyffi scripts tests rundoctest.py py3k
2to3 -w -n py3k/pyffi


