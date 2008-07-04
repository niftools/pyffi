"""Spell for testing the writing of cgf files."""

from tempfile import TemporaryFile

from PyFFI.Formats.CGF import CgfFormat

def testFile(stream,
             version = None, user_version = None,
             filetype = None, chunks = None, versions = None, **kwargs):
    """Writes back the file to a temporary file and raises StandardError if
    sizes differ.

    @param stream: The parsed file.
    @type stream: file
    @param version: The version number.
    @type version: int
    @param user_version: The user version number.
    @type user_version: int
    @param filetype: The file type, L{FileType.GEOM} or L{FileType.ANIM}.
    @type filetype: int
    @param chunks: The file chunks.
    @type chunks: list of L{CgfFormat.Chunk}s
    @param versions: The file chunk versions. If C{None} then these will
        be automatically obtained through L{getChunkVersions}.
    @type versions: list of ints
    @param verbose: The level of verbosity.
    @type verbose: int
    """
    verbose = kwargs.get("verbose")
    f_tmp = TemporaryFile()
    try:
        if verbose:
            print("  writing to temporary file...")
        total_padding = CgfFormat.write(
            f_tmp,
            version = version, user_version = user_version,
            filetype = filetype, chunks = chunks, versions = versions)
        # comparing the files will usually be different because blocks may
        # have been written back in a different order, so cheaply just compare
        # file sizes
        if verbose:
            print("  comparing sizes...")
        stream.seek(0,2)
        f_tmp.seek(0,2)
        if stream.tell() != f_tmp.tell():
            print "original size: %i" % stream.tell()
            print "written size:  %i" % f_tmp.tell()
            print "padding:       %i" % total_padding
            if stream.tell() > f_tmp.tell() or stream.tell() + total_padding < f_tmp.tell():
                f_tmp.seek(0)
                f_debug = open("debug.cgf", "wb")
                f_debug.write(f_tmp.read(-1))
                f_debug.close()
                raise StandardError('write check failed: file sizes differ by more than padding')
    finally:
        f_tmp.close()
