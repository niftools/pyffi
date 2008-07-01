"""Transform MANIFEST into an NSIS file list."""

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
            dir = "."
        else:
            dir = line[:idx]
        file = line[idx+1:]
        # add it to the dictionary
        if not dir in filedict:
            filedict[dir] = []
        filedict[dir].append(file)

    return filedict

def removeslashdot(path):
    return path.replace("\\.", "")

def writeinstallnsh(filedict, nsh):
    nsh.write("!macro InstallManifestFiles\n")
    for dir in sorted(filedict.keys()):
        nsh.write(removeslashdot("  SetOutPath $INSTDIR\\%s\n" % dir))
        nsh.writelines([removeslashdot("  File ..\\%s\\%s\n" % (dir, file))
                       for file in sorted(filedict[dir])])
    nsh.write("!macroend")

manifest = open("MANIFEST", "r")
nsh = open("win-install/manifest.nsh", "w")
try:
    filedict = getfiledict(manifest)
    writeinstallnsh(filedict, nsh)
finally:
    nsh.close()
    manifest.close()

