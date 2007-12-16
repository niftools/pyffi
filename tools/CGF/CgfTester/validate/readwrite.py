# writes back the file and raises StandardError if sizes differ

from PyFFI.CGF import CgfFormat
from tempfile import TemporaryFile

def testFile(stream,
             filetype = None, fileversion = None,
             chunks = None, versions = None, **kwargs):
    f_tmp = TemporaryFile()
    try:
        CgfFormat.write(
            f_tmp,
            filetype = filetype, fileversion = fileversion,
            chunks = chunks, versions = versions)
        # comparing the files will usually be different because blocks may
        # have been written back in a different order, so cheaply just compare
        # file sizes
        stream.seek(0,2)
        f_tmp.seek(0,2)
        if stream.tell() != f_tmp.tell():
            print "original size: %i" % stream.tell()
            print "written size:  %i" % f_tmp.tell()
            try:
                f_tmp.seek(0)
                f_debug = open("debug.cgf", "wb")
                f_debug.write(f_tmp.read(-1))
                f_debug.close()
            except:
                raise
            raise StandardError('write check failed: file sizes differ')
    finally:
        f_tmp.close()
