# dump contents of file to screen

def testFile(filetype, fileversion, f, chunks, versions, verbose):
    for i, (chunk, version) in enumerate(zip(chunks, versions)):
        print 'chunk %3i (%s version 0x%04X)'%(i, chunk.__class__.__name__,version)
        print chunk

