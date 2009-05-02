@echo off

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

del docs\*.*
%PYTHONPATH%\python.exe %PYTHONPATH%\Scripts\epydoc.py  -v --output=docs --name="Python File Format Interface" --url="http://pyffi.sourceforge.net/" --navlink="&nbsp;&nbsp;&nbsp;<a class=\"navbar\" target=\"_top\" href=\"http://pyffi.sourceforge.net/\">Python File Format Interface</a>&nbsp;&nbsp;&nbsp;</th><th class=\"navbar\" align=\"center\">&nbsp;&nbsp;&nbsp;<a class=\"navbar\" target=\"_top\" href=\"http://sourceforge.net\"><img src=\"http://sflogo.sourceforge.net/sflogo.php?group_id=199269\" width=\"88\" height=\"31\" border=\"0\" alt=\"SourceForge.net Logo\" /></a>&nbsp;&nbsp;&nbsp;" --top=pyffi pyffi

del MANIFEST
%PYTHONPATH%\python.exe setup.py sdist --format=zip
rem on windows bztar format is not supported
rem %PYTHONPATH%\python.exe setup.py sdist --format=bztar

%PYTHONPATH%\python.exe makensis.py
rem del win-install\pyffi-*.exe
if exist "%PROGRAMFILES%\NSIS\makensis.exe" "%PROGRAMFILES%\NSIS\makensis.exe" /v3 win-install\pyffi.nsi
if exist "%PROGRAMFILES(x86)%\NSIS\makensis.exe" "%PROGRAMFILES(x86)%\NSIS\makensis.exe" /v3 win-install\pyffi.nsi

:end
pause
