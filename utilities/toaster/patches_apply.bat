@echo off
rem
rem For each file in patches/ (or in its subdirectories) checks if there is a
rem similarly named file in in/ and if so, writes a patched file to out/
rem
"PYTHONPATH\python.exe" "PYTHONPATH\Scripts\patches_apply.py" ..\..\external\apply_patch.bat in out patches
pause
