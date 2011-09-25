@echo off
rem
rem Optimizes all nifs in
rem
rem   in/*.nif
rem
rem to
rem
rem   out/*.nif
rem

title PyFFI Oblivion Optimize - Pass 1
echo.
echo.   Pass 1 - General optimization (filter 1):
echo.
echo.       Running PyFFI optimize ...
"PYTHONPATH\python.exe" "PYTHONPATH\Scripts\niftoaster.py" --ini-file default.ini --ini-file oblivion_optimize_01.ini --noninteractive > oblivion_optimize_01.log 2>&1
echo.
echo.   Done.

title PyFFI Oblivion Optimize - Pass 2
echo.
echo.   Pass 2 - General optimization (filter 2):
echo.
echo.       Running PyFFI optimize ...
"PYTHONPATH\python.exe" "PYTHONPATH\Scripts\niftoaster.py" --ini-file default.ini --ini-file oblivion_optimize_02.ini --noninteractive > oblivion_optimize_02.log 2>&1
echo.
echo.   Done.

title PyFFI Oblivion Optimize - Pass 3
echo.
echo.   Pass 3 - Fixing texture paths:
echo.
echo.       Running PyFFI fix_texturepath ...
"PYTHONPATH\python.exe" "PYTHONPATH\Scripts\niftoaster.py" --ini-file default.ini --ini-file oblivion_optimize_03.ini --noninteractive > oblivion_optimize_03.log 2>&1
echo.
echo.   Done.

title PyFFI Oblivion Optimize - Done
echo.
echo.
echo. You can close this window now.
echo.
echo.
pause
