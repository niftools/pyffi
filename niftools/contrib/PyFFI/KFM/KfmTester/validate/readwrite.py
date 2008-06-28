# writes back the file and raises StandardError if sizes differ

from PyFFI.Formats.KFM import KfmFormat
from tempfile import TemporaryFile

def testFile(stream, version = None,
             header = None, animations = None, footer = None, **args):
    f_tmp = TemporaryFile()
    try:
        KfmFormat.write(
            f_tmp,
            version = version,
            header = header, animations = animations, footer = footer)
        # cheaply just compare file sizes

        stream.seek(0,2)
        f_tmp.seek(0,2)
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
