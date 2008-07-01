;
; PyFFI Self-Installer for Windows
; (PyFFI - http://pyffi.sourceforge.net) 
; (NSIS - http://nsis.sourceforge.net)
;
; Copyright (c) 2007-2008, Python File Format Interface
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

SetCompressor /SOLID lzma

!include "MUI.nsh"

; list of files, generated from MANIFEST file
!include "manifest.nsh"

!define VERSION "1.0.0"

Name "PyFFI ${VERSION}"
Var PYTHONPATH
Var MAYAINST

; define installer pages
!define MUI_ABORTWARNING
!define MUI_FINISHPAGE_NOAUTOCLOSE

; TODO: make header image icons
;!define MUI_HEADERIMAGE
;!define MUI_HEADERIMAGE_BITMAP pyffi_install_150x57.bmp
;!define MUI_HEADERIMAGE_UNBITMAP pyffi_install_150x57.bmp

!define MUI_WELCOMEFINISHPAGE_BITMAP pyffi_install_164x314.bmp
!define MUI_UNWELCOMEFINISHPAGE_BITMAP pyffi_install_164x314.bmp

!define MUI_WELCOMEPAGE_TEXT  "This wizard will guide you through the installation of PyFFI ${VERSION}.\r\n\r\nIt is recommended that you close all other applications, especially any applications that might be running PyFFI, such as Python, QSkope, Blender, or Maya.\r\n\r\nNote to Win2k/XP/Vista users: you require administrator privileges to install PyFFI successfully."
!insertmacro MUI_PAGE_WELCOME

!insertmacro MUI_PAGE_LICENSE ../LICENSE.TXT

!define MUI_DIRECTORYPAGE_TEXT_TOP "Use the field below to specify the folder where you want the documentation files to be copied to. To specify a different folder, type a new name or use the Browse button to select an existing folder."
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Documentation Folder"
!define MUI_DIRECTORYPAGE_VARIABLE $INSTDIR
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES

!define MUI_FINISHPAGE_SHOWREADME
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Show Readme and Changelog"
!define MUI_FINISHPAGE_SHOWREADME_FUNCTION finishShowReadmeChangelog
!define MUI_FINISHPAGE_LINK "Visit us at http://pyffi.sourceforge.net/"
!define MUI_FINISHPAGE_LINK_LOCATION "http://pyffi.sourceforge.net/"
!insertmacro MUI_PAGE_FINISH

!define MUI_WELCOMEPAGE_TEXT  "This wizard will guide you through the uninstallation of PyFFI ${VERSION}.\r\n\r\nBefore starting the uninstallation, make sure PyFFI is not running.\r\n\r\nClick Next to continue."
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages
 
!insertmacro MUI_LANGUAGE "English"
    
;--------------------------------
;Language Strings

;Description
LangString DESC_SecCopyUI ${LANG_ENGLISH} "Copy all required files to the application folder."

;--------------------------------
; Data

OutFile "PyFFI-${VERSION}-windows.exe"
InstallDir "$PROGRAMFILES\PyFFI"
BrandingText "http://pyffi.sourceforge.net/"
Icon nsis1-install.ico
UninstallIcon nsis1-uninstall.ico
ShowInstDetails show
ShowUninstDetails show

;--------------------------------
; Functions

; taken from http://nsis.sourceforge.net/Open_link_in_new_browser_window
# uses $0
Function openLinkNewWindow
  Push $3 
  Push $2
  Push $1
  Push $0
  ReadRegStr $0 HKCR "http\shell\open\command" ""
# Get browser path
    DetailPrint $0
  StrCpy $2 '"'
  StrCpy $1 $0 1
  StrCmp $1 $2 +2 # if path is not enclosed in " look for space as final char
    StrCpy $2 ' '
  StrCpy $3 1
  loop:
    StrCpy $1 $0 1 $3
    DetailPrint $1
    StrCmp $1 $2 found
    StrCmp $1 "" found
    IntOp $3 $3 + 1
    Goto loop
 
  found:
    StrCpy $1 $0 $3
    StrCmp $2 " " +2
      StrCpy $1 '$1"'
 
  Pop $0
  Exec '$1 $0'
  Pop $1
  Pop $2
  Pop $3
FunctionEnd

Function .onInit
  ; check if user is admin
  ; call userInfo plugin to get user info.  The plugin puts the result in the stack
  userInfo::getAccountType

  ; pop the result from the stack into $0
  pop $0

  ; compare the result with the string "Admin" to see if the user is admin. If match, jump 3 lines down.
  strCmp $0 "Admin" +3
  
    ; if there is not a match, print message and return
    messageBox MB_OK "You require administrator privileges to install PyFFI successfully."
    Abort ; quit installer
   
  ; check if Python 2.5 is installed
  ClearErrors
  ReadRegStr $PYTHONPATH HKLM SOFTWARE\Python\PythonCore\2.5\InstallPath ""
  IfErrors 0 python_check_end
  ReadRegStr $PYTHONPATH HKCU SOFTWARE\Python\PythonCore\2.5\InstallPath ""
  IfErrors 0 python_check_end

     ; no key, that means that Python 2.5 is not installed
     MessageBox MB_OK "You need Python 2.5 to use PyFFI. Pressing OK will take you to the Python download page. Please download and run the Python windows installer. When you are done, rerun the PyFFI installer."
     StrCpy $0 "http://www.python.org/download/"
     Call openLinkNewWindow
     Abort ; causes installer to quit

python_check_end:

FunctionEnd

Function finishShowReadmeChangelog
	ExecShell "open" "$INSTDIR\README.TXT"
	ExecShell "open" "$INSTDIR\CHANGELOG.TXT"
FunctionEnd

Section
  SectionIn RO

  ; full PyFFI install takes about 4MB in the Python directory
  ; plus the same for the Maya directory
  ; the build directory takes about 1.5MB
  ; reserve 15MB extra for the installation to be absolutely on
  ; the safe side
  AddSize 15000

  SetShellVarContext all

  ; Clean up old versions and clutter
  RMDir /r "$PYTHONPATH\Lib\site-packages\PyFFI"
  RMDir /r "$PYTHONPATH\Lib\site-packages\NifTester"
  RMDir /r "$PYTHONPATH\Lib\site-packages\NifVis"
  RMDir /r "$PYTHONPATH\Lib\site-packages\KfmTester"
  RMDir /r "$PYTHONPATH\Lib\site-packages\CgfTester"
  RMDir /r "$PYTHONPATH\Lib\site-packages\qskopelib"
  Delete "$PYTHONPATH\Lib\site-packages\PyFFI*.*"
  Delete "$PYTHONPATH\RemovePyFFI.exe"
  Delete "$PYTHONPATH\PyFFI-wininst.log"

  ; Install documentation files
  !insertmacro InstallManifestFiles
  ; Execute install script from installation directory
  SetOutPath $INSTDIR
  ExecWait "$PYTHONPATH\python.exe setup.py install"
  ; remove build and source directories
  RMDir /r "$INSTDIR\build"
  RMDir /r "$INSTDIR\PyFFI"
  RMDir /r "$INSTDIR\scripts"
  Delete "$INSTDIR\setup.py"
  Delete "$INSTDIR\pyffipostinstallation.py"

  ; check if Maya 2008 is installed

  ClearErrors
  ReadRegStr $MAYAINST HKLM SOFTWARE\Autodesk\Maya\2008\Setup\InstallPath "MAYA_INSTALL_LOCATION"
  IfErrors 0 have_maya
  ReadRegStr $MAYAINST HKCU SOFTWARE\Autodesk\Maya\2008\Setup\InstallPath "MAYA_INSTALL_LOCATION"
  IfErrors 0 have_maya
  Goto maya_check_end

have_maya:
    ; key, that means that Maya 2008 is installed
    ; Synchronize PyFFI (CopyFiles does a recursive copy)
    RMDir /r "$MAYAINST\Python\Lib\site-packages\PyFFI"
    CopyFiles "$PYTHONPATH\Lib\site-packages\PyFFI" "$MAYAINST\Python\Lib\site-packages"

maya_check_end:

  ; Clean up possibly previously installed shortcuts
  Delete "$SMPROGRAMS\PyFFI\*.*"

  ; Install shortcuts
  CreateDirectory "$SMPROGRAMS\PyFFI\"
  CreateShortCut "$SMPROGRAMS\PyFFI\Documentation.lnk" "$INSTDIR\docs\index.html"
  CreateShortCut "$SMPROGRAMS\PyFFI\Readme.lnk" "$INSTDIR\README.TXT"
  CreateShortCut "$SMPROGRAMS\PyFFI\ChangeLog.lnk" "$INSTDIR\CHANGELOG.TXT"
  CreateShortCut "$SMPROGRAMS\PyFFI\License.lnk" "$INSTDIR\LICENSE.TXT"
  CreateShortCut "$SMPROGRAMS\PyFFI\Uninstall.lnk" "$INSTDIR\uninstall.exe"

  ; Write the uninstall keys & uninstaller for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PyFFI" "DisplayName" "Python 2.5 PyFFI-${VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\PyFFI" "UninstallString" "$INSTDIR\uninstall.exe"
  SetOutPath $INSTDIR
  WriteUninstaller "uninstall.exe"
SectionEnd

Section "Uninstall"
  SetShellVarContext all
  SetAutoClose false

  ; check if Python 2.5 is installed
  ClearErrors
  ReadRegStr $PYTHONPATH HKLM SOFTWARE\Python\PythonCore\2.5\InstallPath ""
  IfErrors 0 python_remove_pyffi
  ReadRegStr $PYTHONPATH HKCU SOFTWARE\Python\PythonCore\2.5\InstallPath ""
  IfErrors 0 python_remove_pyffi

  Goto python_check_end

python_remove_pyffi:

     ; key, that means that Python 2.5 is still installed
     RMDir /r "$PYTHONPATH\Lib\site-packages\PyFFI"
     Delete "$PYTHONPATH\Lib\site-packages\PyFFI*.*"

python_check_end:

  ; remove registry keys
  DeleteRegKey HKLM SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\PyFFI

  ; remove program files and program directory
  RMDir /r "$INSTDIR"

  ; remove links in start menu
  Delete "$SMPROGRAMS\PyFFI\*.*"
  RMDir "$SMPROGRAMS\PyFFI"
  RMDir "$SMPROGRAMS" ; this will only delete if the directory is empty
SectionEnd
