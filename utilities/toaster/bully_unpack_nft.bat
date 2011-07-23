@echo off
rem
rem Unpacks for instance
rem
rem   in/World/*.nft
rem
rem (or any other nft files in in/) to
rem
rem   in/World/textures/*.dds
rem
"PYTHONPATH\python.exe" "PYTHONPATH\Scripts\niftoaster.py" --ini-file default.ini --ini-file bully_unpack_nft.ini
pause
