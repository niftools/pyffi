@echo off
rem
rem For each file in out/ (or in its subdirectories) checks if there is a
rem similarly named file in in/ and if so, writes a patch to patches/
rem
"PYTHONPATH\python.exe" "PYTHONPATH\Scripts\patches_make.py" ..\..\external\patch_make.bat in out patches
pause
