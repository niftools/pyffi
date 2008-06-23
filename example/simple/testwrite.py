from simple import SimpleFormat
x = SimpleFormat.Example()
x.numIntegers = 5
x.integers.updateSize()
x.integers[0] = 3
x.integers[1] = 1
x.integers[2] = 4
x.integers[3] = 1
x.integers[4] = 5
f = open('pi.simple', 'wb')
x.write(f)
f.close()
