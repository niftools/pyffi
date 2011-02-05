@echo off
rem
rem For each file in in/ (and in its subdirectories) checks if there is a
rem similarly named file in out/ and if so, writes a patch to patch/
rem
"PYTHONPATH\python.exe" "PYTHONPATH\Scripts\patch_recursive_make.py" ..\..\external\patch_make.bat in out patch
pause
