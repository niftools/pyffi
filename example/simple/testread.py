from simple import SimpleFormat
x = SimpleFormat.Example()
f = open('somefile.simple', 'rb')
x.read(f)
f.close()
print x
