# writes back the file and raises StandardError if sizes differ

from PyFFI.Formats.CGF import CgfFormat
from tempfile import TemporaryFile

def testFile(stream,
             filetype = None, fileversion = None, game = None,
             chunks = None, versions = None, **kwargs):
    f_tmp = TemporaryFile()
    try:
        total_padding = CgfFormat.write(
            f_tmp,
            filetype = filetype, fileversion = fileversion, game = game,
            chunks = chunks, versions = versions)
        # comparing the files will usually be different because blocks may
        # have been written back in a different order, so cheaply just compare
        # file sizes
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
