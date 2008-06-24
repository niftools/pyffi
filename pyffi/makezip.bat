@echo off

del MANIFEST

rem find python
set PYTHONPATH=
for /f "tokens=3* delims=	 " %%A in ('reg.exe query "HKLM\SOFTWARE\Python\PythonCore\2.5\InstallPath\" \ve') do set PYTHONPATH="%%B"
rem TODO fix for Vista
if not defined PYTHONPATH (
set PYTHONPATH=C:\Python25
)

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

%PYTHONPATH%\python.exe setup.py sdist --format=zip
%PYTHONPATH%\python.exe setup.py sdist --format=bztar
%PYTHONPATH%\python.exe setup.py bdist_wininst --install-script pyffipostinstallation.py --bitmap pyffi_install_152x261.bmp

:end
pause