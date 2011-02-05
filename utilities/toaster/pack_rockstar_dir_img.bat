@echo off
rem
rem Packs for instance
rem
rem   out/World/*.*
rem
rem (or any other non-empty folder in out/) to
rem
rem   archive_out/World.dir
rem   archive_out/World.img
rem
"PYTHONPATH\python.exe" "PYTHONPATH\Scripts\rockstar_pack_dir_img.py" out archive_out
pause
