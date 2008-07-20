"""Spell for testing the writing of nif files."""

from PyFFI.Formats.NIF import NifFormat
from tempfile import TemporaryFile

def testFile(stream, version = None, user_version = None, roots = None,
             **kwargs):
    """Write back the file to a temporary file and raises StandardError if
    sizes differ.

    @param stream: The stream to which to write.
    @type stream: file
    @param version: The version number.
    @type version: int
    @param user_version: The user version number.
    @type user_version: int
    @param roots: The list of roots of the NIF tree.
    @type roots: list of L{NifFormat.NiObject}s
    @keyword verbose: The level of verbosity.
    @type verbose: int
    """
    verbose = kwargs.get("verbose", 0)
    f_tmp = TemporaryFile()
    try:
        if verbose:
            print("  writing to temporary file...")
        NifFormat.write(
            f_tmp,
            version = version, user_version = user_version, roots = roots)
        # comparing the files will usually be different because blocks may
        # have been written back in a different order, so cheaply just compare
        # file sizes

        # header size can be different due to export info
        # so first read original header
        stream.seek(0)
        orig_hdr = NifFormat.Header()
        orig_hdr.read(stream, version = version, user_version = user_version)
        orig_hdr_size = orig_hdr.getSize(version = version, user_version = user_version)
        f_tmp.seek(0)
        tmp_hdr = NifFormat.Header()
        tmp_hdr.read(f_tmp, version = version, user_version = user_version)
        tmp_hdr_size = tmp_hdr.getSize(version = version, user_version = user_version)

        stream.seek(0, 2)
        f_tmp.seek(0, 2)
        if stream.tell() - orig_hdr_size != f_tmp.tell() - tmp_hdr_size:
            print "original size (excluding header): %i" % (stream.tell() - orig_hdr_size)
            print "written size (excluding header):  %i" % (f_tmp.tell() - tmp_hdr_size)
            f_tmp.seek(0)
            f_debug = open("debug.nif", "wb")
            f_debug.write(f_tmp.read(-1))
            f_debug.close()
            raise StandardError('write check failed: file sizes differ')
    finally:
        f_tmp.close()
