@echo off
rem
rem Unpacks for instance
rem
rem   archive_in/World.dir
rem   archive_in/World.img
rem
rem (or any other .dir/.img files in archive_in/) to
rem
rem   in/World/*.*
rem
"PYTHONPATH\python.exe" "PYTHONPATH\Scripts\rockstar_unpack_dir_img.py" archive_in in
pause
