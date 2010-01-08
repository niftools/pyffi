;
; PyFFI Extra Header for Self-Installer for Windows
; (PyFFI - http://pyffi.sourceforge.net) 
; (NSIS - http://nsis.sourceforge.net)
;
; Copyright (c) 2007-2009, Python File Format Interface
; All rights reserved.
; 
; Redistribution and use in source and binary forms, with or without
; modification, are permitted provided that the following conditions are
; met:
; 
;     * Redistributions of source code must retain the above copyright
;       notice, this list of conditions and the following disclaimer.
;     * Redistributions in binary form must reproduce the above copyright
;       notice, this list of conditions and the following disclaimer in the
;       documentation ; and/or other materials provided with the
;       distribution.
;     * Neither the name of the Python File Format Interface project
;       nor the names of its contributors may be used to endorse or promote
;       products derived from this software without specific prior written
;       permission.
; 
; THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
; IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
; THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
; PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
; CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
; EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
; PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
; PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
; LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
; NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
; SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 

Section Documentation Documentation
  ; first clean up old files
  RMDir /r "$INSTDIR\docs"
  RMDir /r "$INSTDIR\examples"
  RMDir /r "$INSTDIR\tests"

  ; now install new stuff
  SetOutPath $INSTDIR
  File /r ${MISC_SRCDIR}\examples
  File /r ${MISC_SRCDIR}\tests
  File /r ${MISC_SRCDIR}\docs
SectionEnd

Section un.Documentation
  RMDir /r "$INSTDIR\docs"
  RMDir /r "$INSTDIR\examples"
  RMDir /r "$INSTDIR\tests"
SectionEnd

Function unix2dos
    ; strips all CRs
    ; and then converts all LFs into CRLFs
    ; (this is roughly equivalent to "cat file | dos2unix | unix2dos")
    ;
    ; usage:
    ;    Push "infile"
    ;    Push "outfile"
    ;    Call unix2dos
    ;
    ; beware: 
    ; - this function destroys $0 $1 $2
    ; - make sure that infile is *not* equal to outfile

    ClearErrors

    Pop $2
    FileOpen $1 $2 w 

    Pop $2
    FileOpen $0 $2 r

    Push $2 ; save name for deleting

    IfErrors unix2dos_done ; failed to open file for reading or writing

    ; $0 = file input (opened for reading)
    ; $1 = file output (opened for writing)

unix2dos_loop:
    ; read a byte (stored in $2)
    FileReadByte $0 $2
    IfErrors unix2dos_done ; EOL
    ; skip CR
    StrCmp $2 13 unix2dos_loop
    ; if LF write an extra CR
    StrCmp $2 10 unix2dos_cr unix2dos_write

unix2dos_cr:
    FileWriteByte $1 13

unix2dos_write:
    ; write byte
    FileWriteByte $1 $2
    ; read next byte
    Goto unix2dos_loop

unix2dos_done:

    ; close files
    FileClose $0
    FileClose $1

    ; delete original
    Pop $0
    Delete $0

FunctionEnd

!macro InstallFilesExtra
!macroend

; $0 = install path (typically, C:\PythonXX\Lib\site-packages)
; $1 = python executable (typically, python.exe)
; $2 = python version (e.g. "2.6")
!macro UninstallFilesExtra
  RMDir /r "$0\Lib\site-packages\PyFFI"
  RMDir /r "$0\Lib\site-packages\pyffi"
  RMDir /r "$0\Lib\site-packages\NifTester"
  RMDir /r "$0\Lib\site-packages\NifVis"
  RMDir /r "$0\Lib\site-packages\KfmTester"
  RMDir /r "$0\Lib\site-packages\CgfTester"
  RMDir /r "$0\Lib\site-packages\qskopelib"
  Delete "$0\Lib\site-packages\PyFFI*.egg-info"
  Delete "$0\Lib\site-packages\pyffi*.egg-info"
  Delete "$0\RemovePyFFI.exe"
  Delete "$0\Removepyffi.exe"
  Delete "$0\PyFFI-wininst.log"
  Delete "$0\pyffi-wininst.log"
  Delete "$0\Scripts\qskope.*"
  Delete "$0\Scripts\cgftoaster.*"
  Delete "$0\Scripts\kfmtoaster.*"
  Delete "$0\Scripts\ffvt3rskinpartition.*"
  Delete "$0\Scripts\nifdump.*"
  Delete "$0\Scripts\nifmakehsl.*"
  Delete "$0\Scripts\nifoptimize.*"
  Delete "$0\Scripts\niftemplate.*"
  Delete "$0\Scripts\niftexdump.*"
  Delete "$0\Scripts\niftoaster.*"
  Delete "$0\Scripts\pyffipostinstallation.*"
  Delete "$0\Scripts\nifvisualizer.*"
  Delete "$0\Scripts\crydaefilter.*"
!macroend

; checks for installed Python
; if found, path is stored in $0 and a jump is performed
!macro PostExtraPyPathCheck label if_found
  !ifdef HAVE_SECTION_${label}
  SectionGetFlags ${section_${label}} $0
  IntOp $1 $0 & ${SF_SELECTED}
  StrCmp $1 ${SF_SELECTED} 0 extra_py_path_check_not_found_${label}
  StrCpy $0 $PATH_${label}
  StrCmp $0 "" 0 ${if_found}
extra_py_path_check_not_found_${label}:
  !endif
!macroend

!macro PostExtraLegacyKeys label py_version
  !ifdef HAVE_SECTION_${label}
  SectionGetFlags ${section_${label}} $0
  IntOp $1 $0 & ${SF_SELECTED}
  StrCmp $1 ${SF_SELECTED} 0 legacykeys_end_${label}
  ; Write the uninstall keys & uninstaller for Windows
  SetRegView 32
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PyFFI-py${py_version}" "DisplayName" "Python ${py_version} PyFFI-${PRODUCT_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PyFFI-py${py_version}" "UninstallString" "$INSTDIR\PyFFI_uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PyFFI-py${py_version}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PyFFI-py${py_version}" "Publisher" "Python File Format Interface"
legacykeys_end_${label}:
  !endif
!macroend

!macro PostExtra
  SetOutPath $INSTDIR
  File ${MISC_SRCDIR}\README.rst
  File ${MISC_SRCDIR}\INSTALL.rst
  File ${MISC_SRCDIR}\LICENSE.rst
  File ${MISC_SRCDIR}\CHANGELOG.rst
  File ${MISC_SRCDIR}\AUTHORS.rst
  File ${MISC_SRCDIR}\TODO.rst
  File ${MISC_SRCDIR}\THANKS.rst
  File ${MISC_SRCDIR}\CONTRIBUTE.rst

  ; Windows does not recognize the rst extension, so copy to TXT
  ; At the same time, force Windows style line endings.
  Push "$INSTDIR\README.rst"
  Push "$INSTDIR\README.txt"
  Call unix2dos
  Push "$INSTDIR\CHANGELOG.rst"
  Push "$INSTDIR\CHANGELOG.txt"
  Call unix2dos
  Push "$INSTDIR\AUTHORS.rst"
  Push "$INSTDIR\AUTHORS.txt"
  Call unix2dos
  Push "$INSTDIR\LICENSE.rst"
  Push "$INSTDIR\LICENSE.txt"
  Call unix2dos
  Push "$INSTDIR\INSTALL.rst"
  Push "$INSTDIR\INSTALL.txt"
  Call unix2dos
  Push "$INSTDIR\THANKS.rst"
  Push "$INSTDIR\THANKS.txt"
  Call unix2dos
  Push "$INSTDIR\TODO.rst"
  Push "$INSTDIR\TODO.txt"
  Call unix2dos
  Push "$INSTDIR\CONTRIBUTE.rst"
  Push "$INSTDIR\CONTRIBUTE.txt"
  Call unix2dos

  ; Install shortcuts
  CreateDirectory "$SMPROGRAMS\PyFFI\"
  CreateShortCut "$SMPROGRAMS\PyFFI\Authors.lnk" "$INSTDIR\AUTHORS.txt"
  CreateShortCut "$SMPROGRAMS\PyFFI\ChangeLog.lnk" "$INSTDIR\CHANGELOG.txt"
  CreateShortCut "$SMPROGRAMS\PyFFI\Documentation.lnk" "$INSTDIR\docs\index.html"
  CreateShortCut "$SMPROGRAMS\PyFFI\License.lnk" "$INSTDIR\LICENSE.txt"
  CreateShortCut "$SMPROGRAMS\PyFFI\Readme.lnk" "$INSTDIR\README.txt"
  CreateShortCut "$SMPROGRAMS\PyFFI\Thanks.lnk" "$INSTDIR\THANKS.txt"
  CreateShortCut "$SMPROGRAMS\PyFFI\Todo.lnk" "$INSTDIR\TODO.txt"
  CreateShortCut "$SMPROGRAMS\PyFFI\Contribute.lnk" "$INSTDIR\CONTRIBUTE.txt"
  CreateShortCut "$SMPROGRAMS\PyFFI\Uninstall.lnk" "$INSTDIR\uninstall.exe"

  !insertmacro PostExtraLegacyKeys python_2_5_32 2.5
  !insertmacro PostExtraLegacyKeys python_2_6_32 2.6

  !insertmacro PostExtraPyPathCheck python_3_2_64 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_2_32 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_1_64 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_1_32 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_0_64 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_0_32 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_2_7_64 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_2_7_32 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_2_6_64 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_2_6_32 install_shortcuts
  ; 2.5 64 bit has problem with xml support
  ;!insertmacro PostExtraPyPathCheck python_2_5_64 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_2_5_32 install_shortcuts

  ; No version of python installed which can run qskope.
  MessageBox MB_OK "A version of Python which can run qskope/niftoaster was not found: shortcuts will not be created."
  GoTo install_shortcuts_end

install_shortcuts:

  ; QSkope desktop shortcut
  CreateShortCut "$DESKTOP\QSkope.lnk" "$0\python.exe" "$0\Scripts\qskope.py" "" "" "" "" "QSkope"

  ; Set up file associations
  SetRegView 32
  WriteRegStr HKCR ".nif" "" "NetImmerseFile"
  WriteRegStr HKCR ".nifcache" "" "NetImmerseFile"
  WriteRegStr HKCR ".kf" "" "NetImmerseFile"
  WriteRegStr HKCR ".kfa" "" "NetImmerseFile"
  WriteRegStr HKCR ".kfm" "" "NetImmerseFile"

    WriteRegStr HKCR "NetImmerseFile" "" "NetImmerse/Gamebryo File"
    WriteRegStr HKCR "NetImmerseFile\shell" "" "open"

    WriteRegStr HKCR "NetImmerseFile\shell\Optimize with PyFFI" "" ""
    WriteRegStr HKCR "NetImmerseFile\shell\Optimize with PyFFI\command" "" '"$0\python.exe" "$0\Scripts\niftoaster.py" optimize --pause "%1"'

    WriteRegStr HKCR "Folder\shell\Optimize with PyFFI" "" ""
    WriteRegStr HKCR "Folder\shell\Optimize with PyFFI\command" "" '"$0\python.exe" "$0\Scripts\niftoaster.py" optimize --pause "%1"'

    WriteRegStr HKCR "NetImmerseFile\shell\Open with QSkope" "" ""
    WriteRegStr HKCR "NetImmerseFile\shell\Open with QSkope\command" "" '"$0\python.exe" "$0\Scripts\qskope.py" "%1"'

  WriteRegStr HKCR ".cgf" "" "CrytekGeometryFile"
  WriteRegStr HKCR ".chr" "" "CrytekGeometryFile"

    WriteRegStr HKCR "CrytekGeometryFile" "" "Crytek Geometry File"
    WriteRegStr HKCR "CrytekGeometryFile\shell" "" "open"

    WriteRegStr HKCR "CrytekGeometryFile\shell\Open with QSkope" "" ""
    WriteRegStr HKCR "CrytekGeometryFile\shell\Open with QSkope\command" "" '"$0\python.exe" "$0\Scripts\qskope.py" "%1"'

  ; no longer in pyffi
  DeleteRegKey HKCR "daefile\shell\Prepare for CryEngine with PyFFI"

  WriteRegStr HKCR ".dds" "" "DirectX.DDS.Document" ; following DirectX SDK

    WriteRegStr HKCR "DirectX.DDS.Document" "" "DDS Document"
    WriteRegStr HKCR "DirectX.DDS.Document\shell" "" "open"

    WriteRegStr HKCR "DirectX.DDS.Document\shell\Open with QSkope" "" ""
    WriteRegStr HKCR "DirectX.DDS.Document\shell\Open with QSkope\command" "" '"$0\python.exe" "$0\Scripts\qskope.py" "%1"'

install_shortcuts_end:

!macroend

!macro UnPostExtra
  ; Remove registry keys
  SetRegView 32
  DeleteRegKey HKCR "NetImmerseFile\shell\Optimize with PyFFI"
  DeleteRegKey HKCR "Folder\shell\Optimize with PyFFI"
  DeleteRegKey HKCR "NetImmerseFile\shell\Open with QSkope"
  DeleteRegKey HKCR "CrytekGeometryFile\shell\Open with QSkope"
  DeleteRegKey HKCR "DirectX.DDS.Document\shell\Open with QSkope"

  ; Remove legacy registry keys
  DeleteRegKey HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\PyFFI-py2.5"
  DeleteRegKey HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\PyFFI-py2.6"

  ; remove QSkope shortcut
  Delete "$DESKTOP\QSkope.lnk"

  ; Clean up start menu shortcuts
  Delete "$SMPROGRAMS\PyFFI\*.*"
  RMDir "$SMPROGRAMS\PyFFI"

  ; Clean up documentation
  Delete "$INSTDIR\*.TXT"
  Delete "$INSTDIR\*.txt"
  Delete "$INSTDIR\*.rst"
!macroend
