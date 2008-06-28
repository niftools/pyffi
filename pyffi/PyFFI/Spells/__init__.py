"""The PyFFI.Spells module bundles scripts for running hacking, surgery, and
validation tests. It is originally based on wz's NifTester module, although not
much of the original code that is left in this module.

These three functions in the tester script are called:
   testRoot(block)  - will be called on every root block in the file
   testBlock(block) - will be called on every block in the file
   testFile(stream, version, user_version, ...)
                    - will be called on every file
Not all of these three functions need to be present.
"""

import gc

# useful as testFile which simply writes back the file
# but restores the file if the write fails
def testFileOverwrite(*readargs):
    # first argument is always the stream, by convention
    stream = readargs[0]
    stream.seek(0)
    backup = stream.read(-1)
    stream.seek(0)
    if args.get('verbose'):
        print "writing %s..."%stream.name
    try:
        CgfFormat.write(*readargs)
    except: # not just StandardError, also CTRL-C
        print "write failed!!! attempt to restore original file..."
        stream.seek(0)
        stream.write(backup)
        stream.truncate()
        raise
    stream.truncate()

# test all files using testChunk and testFile functions
def testPath(top, format = None, spellmodule = None, verbose = 0, **kwargs):
    """Walk over all files in a directory tree and do a particular test (or
    cast a particular spell) on every file.

    @param top: The directory or file to test.
    @type top: str
    @param format: The format class, such as L{PyFFI.NIF.NifFormat}.
    @type format: L{PyFFI.XmlFileFormat} subclass
    @param spellmodule: The actual spell module.
    @type spellmodule: module
    @param verbose: Level of verbosity.
    @type verbose: int
    @param kwargs: Extra keyword arguments that will be passed to the spell.
    @type kwargs: dict
    """
    raisereaderror = getattr(spellmodule, "__raisereaderror__", False)
    readonly = getattr(spellmodule, "__readonly__", True)
    mode = 'rb' if readonly else 'r+b'
    testRoot = getattr(spellmodule, "testRoot", None)
    testBlock = getattr(spellmodule, "testBlock", None)
    testFile = getattr(spellmodule, "testFile", None)
    spellkwargs = dict(kwargs)
    spellkwargs['verbose'] = verbose

    # remind, fileinfotuple is stream, version, user_version, and anything
    # returned by format.read appended to it
    # these are exactly the arguments accepted by write, so it identifies
    # the file uniquely
    for fileinfotuple in format.walkFile(
        top, raisereaderror = raisereaderror,
        verbose = min(1, verbose), mode = mode):

        # cast all spells
        if testRoot:
            for block in format.getRoots(*fileinfotuple):
                testRoot(block, **spellkwargs)
        if testBlock:
            for block in format.getBlocks(*fileinfotuple):
                testBlock(block, **spellkwargs)
        if testFile:
            testFile(*fileinfotuple, **spellkwargs)

        # save file back to disk if not readonly
        if not readonly:
            testFileOverwrite(*fileinfotuple)

        # force free memory (this helps when parsing many very large files)
        del fileinfotuple
        gc.collect()

