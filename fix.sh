#!/bin/sh

# Automatically fix eol-style and executable flag on files.

find . \( -name "Makefile" -or -name "*.py" -or -name "*.pyx" -or -name "*.c" -or -name "*.cpp" -or -name "*.h" -or -name "*.hpp" -or -name "*.nsi" -or -name "*.nsh" -or -name "*.sh" -or -name "*.xml" -or -name "*.txt" -or -name "*.rst" \) -exec dos2unix {} \;

# must first do dos2unix, to revert mixed eol-style
find . \( -name "*.TXT" -or -name "*.bat" \) -exec dos2unix {} \;
find . \( -name "*.TXT" -or -name "*.bat" \) -exec unix2dos {} \;

find . \( -name "*.exe" -or -name "*.bat" -or -name "*.sh" \) -exec chmod +x {} \;

