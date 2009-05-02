"""Transform MANIFEST into an NSIS file list."""

import sys # python version

import pyffi # version

def getfiledict(stream):
    """Get dictionary mapping each directory to a list of files."""
    filedict = {}
    for line in stream:
        # remove EOL
        line = line.rstrip()
        # windows separators
        line = line.replace('/', '\\')
        # seperate file and path
        idx = line.rfind('\\')
        if idx == -1:
            path = "."
        else:
            path = line[:idx]
        filename = line[idx+1:]
        # add it to the dictionary
        if not path in filedict:
            filedict[path] = []
        filedict[path].append(filename)

    return filedict

def removeslashdot(path):
    return path.replace("\\.", "")

def writeinstallnsh(filedict, nsh):
    nsh.write("!macro InstallManifestFiles\n")
    for path in sorted(filedict.keys()):
        nsh.write(removeslashdot("  SetOutPath $INSTDIR\\%s\n" % path))
        nsh.writelines([removeslashdot("  File ..\\%s\\%s\n" % (path, filename))
                        for filename in sorted(filedict[path])])
    nsh.write("!macroend\n\n")

def writeuninstallnsh(filedict, nsh):
    nsh.write("!macro UninstallManifestFiles\n")
    for path in sorted(filedict.keys()):
        if path.startswith("PyFFI"):
            nsh.writelines([removeslashdot("  Delete $PYTHONPATH\\Lib\\site-packages\\%s\\%s\n"
                                           % (path, filename))
                            for filename in sorted(filedict[path])])
            # .pyc files
            nsh.writelines([removeslashdot("  Delete $PYTHONPATH\\Lib\\site-packages\\%s\\%sc\n"
                                           % (path, filename))
                            for filename in sorted(filedict[path])
                            if filename.endswith(".py")])
            # .pyo files
            nsh.writelines([removeslashdot("  Delete $PYTHONPATH\\Lib\\site-packages\\%s\\%so\n"
                                           % (path, filename))
                            for filename in sorted(filedict[path])
                            if filename.endswith(".py")])
        else:
            nsh.writelines([removeslashdot("  Delete $INSTDIR\\%s\\%s\n"
                                           % (path, filename))
                            for filename in sorted(filedict[path])])
    nsh.write("!macroend\n\n")

manifest = open("MANIFEST", "r")
nsh = open("win-install/manifest.nsh", "w")
try:
    nsh.write("""\
!define VERSION "%s"
!define PYTHONVERSION "%i.%i"

""" % (pyffi.__version__, sys.version_info[0], sys.version_info[1]))
    filedict = getfiledict(manifest)
    writeinstallnsh(filedict, nsh)
    writeuninstallnsh(filedict, nsh)
finally:
    nsh.close()
    manifest.close()
