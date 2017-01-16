;
; PyFFI Extra Header for Self-Installer for Windows
; (PyFFI - https://github.com/niftools/pyffi)
; (NSIS - http://nsis.sourceforge.net)
;
; Copyright (c) 2007-2012, Python File Format Interface
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

; from http://nsis.sourceforge.net/StrRep
!define StrRep "!insertmacro StrRep"
!macro StrRep output string old new
    Push "${string}"
    Push "${old}"
    Push "${new}"
    !ifdef __UNINSTALL__
        Call un.StrRep
    !else
        Call StrRep
    !endif
    Pop ${output}
!macroend
 
!macro Func_StrRep un
    Function ${un}StrRep
        Exch $R2 ;new
        Exch 1
        Exch $R1 ;old
        Exch 2
        Exch $R0 ;string
        Push $R3
        Push $R4
        Push $R5
        Push $R6
        Push $R7
        Push $R8
        Push $R9
 
        StrCpy $R3 0
        StrLen $R4 $R1
        StrLen $R6 $R0
        StrLen $R9 $R2
        loop:
            StrCpy $R5 $R0 $R4 $R3
            StrCmp $R5 $R1 found
            StrCmp $R3 $R6 done
            IntOp $R3 $R3 + 1 ;move offset by 1 to check the next character
            Goto loop
        found:
            StrCpy $R5 $R0 $R3
            IntOp $R8 $R3 + $R4
            StrCpy $R7 $R0 "" $R8
            StrCpy $R0 $R5$R2$R7
            StrLen $R6 $R0
            IntOp $R3 $R3 + $R9 ;move offset by length of the replacement string
            Goto loop
        done:
 
        Pop $R9
        Pop $R8
        Pop $R7
        Pop $R6
        Pop $R5
        Pop $R4
        Pop $R3
        Push $R0
        Push $R1
        Pop $R0
        Pop $R1
        Pop $R0
        Pop $R2
        Exch $R1
    FunctionEnd
!macroend
!insertmacro Func_StrRep ""
; XXX not used
;!insertmacro Func_StrRep "un."

; from http://nsis.sourceforge.net/ReplaceInFile
!macro ReplaceInFile SOURCE_FILE SEARCH_TEXT REPLACEMENT
  Push "${SOURCE_FILE}"
  Push "${SEARCH_TEXT}"
  Push "${REPLACEMENT}"
  Call RIF
!macroend

Function RIF
 
  ClearErrors  ; want to be a newborn
 
  Exch $0      ; REPLACEMENT
  Exch
  Exch $1      ; SEARCH_TEXT
  Exch 2
  Exch $2      ; SOURCE_FILE
 
  Push $R0     ; SOURCE_FILE file handle
  Push $R1     ; temporary file handle
  Push $R2     ; unique temporary file name
  Push $R3     ; a line to sar/save
  Push $R4     ; shift puffer
 
  IfFileExists $2 +1 RIF_error      ; knock-knock
  FileOpen $R0 $2 "r"               ; open the door
 
  GetTempFileName $R2               ; who's new?
  FileOpen $R1 $R2 "w"              ; the escape, please!
 
  RIF_loop:                         ; round'n'round we go
    FileRead $R0 $R3                ; read one line
    IfErrors RIF_leaveloop          ; enough is enough
    RIF_sar:                        ; sar - search and replace
      Push "$R3"                    ; (hair)stack
      Push "$1"                     ; needle
      Push "$0"                     ; blood
      Call StrRep                   ; do the bartwalk
      StrCpy $R4 "$R3"              ; remember previous state
      Pop $R3                       ; gimme s.th. back in return!
      StrCmp "$R3" "$R4" +1 RIF_sar ; loop, might change again!
    FileWrite $R1 "$R3"             ; save the newbie
  Goto RIF_loop                     ; gimme more
 
  RIF_leaveloop:                    ; over'n'out, Sir!
    FileClose $R1                   ; S'rry, Ma'am - clos'n now
    FileClose $R0                   ; me 2
 
    ; XXX no backup
    ;Delete "$2.old"                 ; go away, Sire
    ;Rename "$2" "$2.old"            ; step aside, Ma'am
    ;Rename "$R2" "$2"               ; hi, baby!
    Delete "$2"                     ; go away, Sire
    Rename "$R2" "$2"               ; hi, baby!
 
    ClearErrors                     ; now i AM a newborn
    Goto RIF_out                    ; out'n'away
 
  RIF_error:                        ; ups - s.th. went wrong...
    SetErrors                       ; ...so cry, boy!
 
  RIF_out:                          ; your wardrobe?
  Pop $R4
  Pop $R3
  Pop $R2
  Pop $R1
  Pop $R0
  Pop $2
  Pop $0
  Pop $1
 
FunctionEnd

; custom sections

Section Documentation Documentation
  ; first clean up old files
  RMDir /r "$INSTDIR\docs"
  RMDir /r "$INSTDIR\examples"
  RMDir /r "$INSTDIR\tests"

  ; now install new stuff
  SetOutPath "$INSTDIR\examples\"
  File /r "${MISC_SRCDIR}\examples\"
  SetOutPath "$INSTDIR\tests\"
  File /r "${MISC_SRCDIR}\tests\"
  SetOutPath "$INSTDIR\docs\"
  File /r "${MISC_SRCDIR}\docs\"
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
  StrCmp $1 ${SF_SELECTED} 0 extra_py_path_check_not_found_${label}_${if_found}
  StrCpy $0 $PATH_${label}
  StrCmp $0 "" 0 ${if_found}
extra_py_path_check_not_found_${label}_${if_found}:
  !endif
!macroend

!macro PostExtra
  SetOutPath "$INSTDIR"
  File "${MISC_SRCDIR}\README.rst"
  File "${MISC_SRCDIR}\INSTALL.rst"
  File "${MISC_SRCDIR}\LICENSE.rst"
  File "${MISC_SRCDIR}\CHANGELOG.rst"
  File "${MISC_SRCDIR}\AUTHORS.rst"
  File "${MISC_SRCDIR}\TODO.rst"
  File "${MISC_SRCDIR}\THANKS.rst"
  File "${MISC_SRCDIR}\CONTRIBUTE.rst"

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

  SetOutPath "$INSTDIR\utilities\toaster"
  File /oname=default.ini.tmp "${MISC_SRCDIR}\utilities\toaster\default.ini"
  File /oname=shell_optimize.ini.tmp "${MISC_SRCDIR}\utilities\toaster\shell_optimize.ini"
  File /oname=oblivion_optimize_01.ini.tmp "${MISC_SRCDIR}\utilities\toaster\oblivion_optimize_01.ini"
  File /oname=oblivion_optimize_02.ini.tmp "${MISC_SRCDIR}\utilities\toaster\oblivion_optimize_02.ini"
  File /oname=oblivion_optimize_03.ini.tmp "${MISC_SRCDIR}\utilities\toaster\oblivion_optimize_03.ini"
  File /oname=oblivion_optimize.bat.tmp "${MISC_SRCDIR}\utilities\toaster\oblivion_optimize.bat"
  File /oname=bully_unpack_nft.ini.tmp "${MISC_SRCDIR}\utilities\toaster\bully_unpack_nft.ini"
  File /oname=bully_unpack_nft.bat.tmp "${MISC_SRCDIR}\utilities\toaster\bully_unpack_nft.bat"
  File /oname=rockstar_unpack_dir_img.bat.tmp "${MISC_SRCDIR}\utilities\toaster\rockstar_unpack_dir_img.bat"
  File /oname=rockstar_pack_dir_img.bat.tmp "${MISC_SRCDIR}\utilities\toaster\rockstar_pack_dir_img.bat"
  File /oname=patch_recursive_make.bat.tmp "${MISC_SRCDIR}\utilities\toaster\patch_recursive_make.bat"
  File /oname=patch_recursive_apply.bat.tmp "${MISC_SRCDIR}\utilities\toaster\patch_recursive_apply.bat"

  SetOutPath "$INSTDIR\external"
  File /oname=patch_make.bat.tmp "${MISC_SRCDIR}\external\patch_make.bat"
  File /oname=patch_apply.bat.tmp "${MISC_SRCDIR}\external\patch_apply.bat"
  File "${MISC_SRCDIR}\external\xdelta3.0z.x86-32.exe"

  CreateDirectory "$INSTDIR\utilities\toaster\in"
  CreateDirectory "$INSTDIR\utilities\toaster\out"
  CreateDirectory "$INSTDIR\utilities\toaster\patch"
  CreateDirectory "$INSTDIR\utilities\toaster\archive_in"
  CreateDirectory "$INSTDIR\utilities\toaster\archive_out"

  ; force CRLF EOL in ini and batch files
  Delete "$INSTDIR\utilities\toaster\default.ini"
  Push "$INSTDIR\utilities\toaster\default.ini.tmp"
  Push "$INSTDIR\utilities\toaster\default.ini"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\shell_optimize.ini"
  Push "$INSTDIR\utilities\toaster\shell_optimize.ini.tmp"
  Push "$INSTDIR\utilities\toaster\shell_optimize.ini"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\oblivion_optimize_01.ini"
  Push "$INSTDIR\utilities\toaster\oblivion_optimize_01.ini.tmp"
  Push "$INSTDIR\utilities\toaster\oblivion_optimize_01.ini"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\oblivion_optimize_02.ini"
  Push "$INSTDIR\utilities\toaster\oblivion_optimize_02.ini.tmp"
  Push "$INSTDIR\utilities\toaster\oblivion_optimize_02.ini"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\oblivion_optimize_03.ini"
  Push "$INSTDIR\utilities\toaster\oblivion_optimize_03.ini.tmp"
  Push "$INSTDIR\utilities\toaster\oblivion_optimize_03.ini"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\oblivion_optimize.bat"
  Push "$INSTDIR\utilities\toaster\oblivion_optimize.bat.tmp"
  Push "$INSTDIR\utilities\toaster\oblivion_optimize.bat"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\bully_unpack_nft.ini"
  Push "$INSTDIR\utilities\toaster\bully_unpack_nft.ini.tmp"
  Push "$INSTDIR\utilities\toaster\bully_unpack_nft.ini"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\bully_unpack_nft.bat"
  Push "$INSTDIR\utilities\toaster\bully_unpack_nft.bat.tmp"
  Push "$INSTDIR\utilities\toaster\bully_unpack_nft.bat"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\rockstar_unpack_dir_img.bat"
  Push "$INSTDIR\utilities\toaster\rockstar_unpack_dir_img.bat.tmp"
  Push "$INSTDIR\utilities\toaster\rockstar_unpack_dir_img.bat"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\rockstar_pack_dir_img.bat"
  Push "$INSTDIR\utilities\toaster\rockstar_pack_dir_img.bat.tmp"
  Push "$INSTDIR\utilities\toaster\rockstar_pack_dir_img.bat"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\patch_recursive_make.bat"
  Push "$INSTDIR\utilities\toaster\patch_recursive_make.bat.tmp"
  Push "$INSTDIR\utilities\toaster\patch_recursive_make.bat"
  Call unix2dos
  Delete "$INSTDIR\utilities\toaster\patch_recursive_apply.bat"
  Push "$INSTDIR\utilities\toaster\patch_recursive_apply.bat.tmp"
  Push "$INSTDIR\utilities\toaster\patch_recursive_apply.bat"
  Call unix2dos
  Delete "$INSTDIR\external\patch_make.bat"
  Push "$INSTDIR\external\patch_make.bat.tmp"
  Push "$INSTDIR\external\patch_make.bat"
  Call unix2dos
  Delete "$INSTDIR\external\patch_apply.bat"
  Push "$INSTDIR\external\patch_apply.bat.tmp"
  Push "$INSTDIR\external\patch_apply.bat"
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
  CreateShortCut "$SMPROGRAMS\PyFFI\Uninstall.lnk" "$INSTDIR\PyFFI_uninstall.exe"

  ; first check 32 bit: PyQt4 can only be installed for these...
  !insertmacro PostExtraPyPathCheck python_3_2_32 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_1_32 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_0_32 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_2_64 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_1_64 install_shortcuts
  !insertmacro PostExtraPyPathCheck python_3_0_64 install_shortcuts

  ; No version of python installed which can run qskope.
  MessageBox MB_OK "A version of Python which can run qskope/niftoaster was not found: shortcuts will not be created and batch files will not run."
  GoTo install_shortcuts_end

install_shortcuts:

  ; set python path in batch files
  !insertmacro ReplaceInFile "$INSTDIR\utilities\toaster\rockstar_pack_dir_img.bat" PYTHONPATH "$0"
  !insertmacro ReplaceInFile "$INSTDIR\utilities\toaster\rockstar_unpack_dir_img.bat" PYTHONPATH "$0"
  !insertmacro ReplaceInFile "$INSTDIR\utilities\toaster\bully_unpack_nft.bat" PYTHONPATH "$0"
  !insertmacro ReplaceInFile "$INSTDIR\utilities\toaster\patch_recursive_make.bat" PYTHONPATH "$0"
  !insertmacro ReplaceInFile "$INSTDIR\utilities\toaster\patch_recursive_apply.bat" PYTHONPATH "$0"
  !insertmacro ReplaceInFile "$INSTDIR\utilities\toaster\oblivion_optimize.bat" PYTHONPATH "$0"

  ; QSkope desktop shortcut
  CreateShortCut "$DESKTOP\QSkope.lnk" '"$0\python.exe"' '"$0\Scripts\qskope.py"' "" "" "" "" "QSkope"

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
    WriteRegStr HKCR "NetImmerseFile\shell\Optimize with PyFFI\command" "" '"$0\python.exe" "$0\Scripts\niftoaster.py" --ini-file="$INSTDIR\utilities\toaster\default.ini" --ini-file="$INSTDIR\utilities\toaster\shell_optimize.ini" --dest-dir= --source-dir= --pause --overwrite "%1"'

    WriteRegStr HKCR "Folder\shell\Optimize with PyFFI" "" ""
    WriteRegStr HKCR "Folder\shell\Optimize with PyFFI\command" "" '"$0\python.exe" "$0\Scripts\niftoaster.py" --ini-file="$INSTDIR\utilities\toaster\default.ini" --ini-file="$INSTDIR\utilities\toaster\shell_optimize.ini" --dest-dir= --source-dir= --pause --overwrite "%1"'

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

  WriteRegStr HKCR ".ini" "" "inifile"

    WriteRegStr HKCR "inifile" "" "Configuration Settings"
    WriteRegStr HKCR "inifile\shell" "" "open"
    WriteRegStr HKCR "inifile\shell\Run PyFFI\command" "" '"$0\python.exe" "$0\Scripts\niftoaster.py" --ini-file="$INSTDIR\utilities\toaster\default.ini" --ini-file="%1"'

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
  DeleteRegKey HKCR "inifile\shell\Run PyFFI"

  ; remove QSkope shortcut
  Delete "$DESKTOP\QSkope.lnk"

  ; Clean up start menu shortcuts
  Delete "$SMPROGRAMS\PyFFI\*.*"
  RMDir "$SMPROGRAMS\PyFFI"

  ; Clean up documentation
  Delete "$INSTDIR\*.TXT"
  Delete "$INSTDIR\*.txt"
  Delete "$INSTDIR\*.rst"
  Delete "$INSTDIR\external\*.*"
  RMDir "$INSTDIR\external"
  Delete "$INSTDIR\utilities\toaster\*.*"
  RMDir "$INSTDIR\utilities\toaster\archive_in"
  RMDir "$INSTDIR\utilities\toaster\archive_out"
  RMDir "$INSTDIR\utilities\toaster\patch"
  RMDir "$INSTDIR\utilities\toaster\in"
  RMDir "$INSTDIR\utilities\toaster\out"
  RMDir "$INSTDIR\utilities\toaster"
  RMDir "$INSTDIR\utilities"
!macroend

