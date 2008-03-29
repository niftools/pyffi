@rem quick pyffi doctest batch file

@echo off

rem find python
set PYTHONPATH=
for /f "tokens=3* delims=	 " %%A in ('reg.exe query "HKLM\SOFTWARE\Python\PythonCore\2.5\InstallPath\" \ve') do set PYTHONPATH="%%B"

rem not found... complain and quit
if not defined PYTHONPATH (
echo.
echo Python 2.5 not found!
echo.
goto end
)

rem python in registry but executable not found... complain and exit
if not exist %PYTHONPATH%\python.exe (
echo.
echo python.exe not found!
echo.
goto end
)

rem run the installation from the setup script
%PYTHONPATH%\python.exe rundoctest.py

:end

rem remove local variables
set PYTHONPATH=

pause
