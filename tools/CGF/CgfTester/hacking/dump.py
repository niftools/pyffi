# dump contents of file to screen

def testFile(stream, filetype = None, fileversion = None, game = None, chunks = None, versions = None, verbose = None):
    for i, (chunk, version) in enumerate(zip(chunks, versions)):
        print 'chunk %3i (%s version 0x%04X)'%(i, chunk.__class__.__name__,version)
        print chunk
