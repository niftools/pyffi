#!/bin/sh

git clean -x -d -f
../Python-3.1.2/python ../Python-3.1.2/Tools/scripts/2to3 -w -n pyffi examples scripts rundoctest.py setup.py
find tests/ -name "*.txt" | xargs ../Python-3.1.2/python ../Python-3.1.2/Tools/scripts/2to3 -w -n -d
#../Python-3.1.2/python rundoctest.py

