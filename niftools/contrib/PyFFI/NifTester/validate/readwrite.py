# writes back the file and raises StandardError if sizes differ

from PyFFI.NIF import NifFormat
from tempfile import TemporaryFile

def testFile(stream, version = None, user_version = None, roots = None, **args):
    f_tmp = TemporaryFile()
    try:
        NifFormat.write(
            f_tmp,
            version = version, user_version = user_version, roots = roots)
        # comparing the files will usually be different because blocks may
        # have been written back in a different order, so cheaply just compare
        # file sizes
        stream.seek(0,2)
        f_tmp.seek(0,2)
        if stream.tell() != f_tmp.tell():
            print "original size: %i" % stream.tell()
            print "written size:  %i" % f_tmp.tell()
            raise StandardError('write check failed: file sizes differ')
    finally:
        f_tmp.close()
