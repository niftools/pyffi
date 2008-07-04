"""Spell for testing the writing of kfm files."""

from tempfile import TemporaryFile

from PyFFI.Formats.KFM import KfmFormat

def testFile(stream, version = None, user_version = None,
             header = None, animations = None, footer = None, **args):
    """Write back the file to a temporary file and raises StandardError if
    sizes differ.

    @param stream: The parsed file.
    @type stream: file
    @param version: The version of the parsed file.
    @type version: int
    @param user_version: The user version of the parsed file.
    @type user_version: int
    @param header: The kfm header.
    @type header: L{KfmFormat.Header}
    @param animations: The animation data.
    @type animations: list of L{KfmFormat.Animation}
    @param footer: The kfm footer.
    @type footer: L{KfmFormat.Footer}
    """
    f_tmp = TemporaryFile()
    try:
        KfmFormat.write(
            f_tmp,
            version = version, user_version = user_version,
            header = header, animations = animations, footer = footer)
        # cheaply just compare file sizes

        stream.seek(0, 2)
        f_tmp.seek(0, 2)
        if stream.tell() != f_tmp.tell():
            print "original size: %i" % (stream.tell())
            print "written size:  %i" % (f_tmp.tell())
            f_tmp.seek(0)
            f_debug = open("debug.kfm", "wb")
            f_debug.write(f_tmp.read(-1))
            f_debug.close()
            raise StandardError('write check failed: file sizes differ')
    finally:
        f_tmp.close()

