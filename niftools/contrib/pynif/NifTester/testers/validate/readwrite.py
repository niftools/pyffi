# writes back the file and raises StandardError if sizes differ

from PyFFI.NIF import NifFormat
from tempfile import TemporaryFile

def testFile(version, user_version, f, roots, verbose):
    f_tmp = TemporaryFile()
    try:
        NifFormat.write(version, user_version, f_tmp, roots)
        f.seek(2,0)
        f_tmp.seek(2,0)
        # comparing the files will usually be different because blocks may
        # have been written back in a different order, so cheaply just compare
        # file sizes
        if f.tell() != f_tmp.tell():
            raise StandardError('write check failed: file sizes differ')
    finally:
        f_tmp.close()
