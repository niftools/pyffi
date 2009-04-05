def testFile(stream, version = None,
             header = None, animations = None, footer = None,
             **args):
    print(header)
    for anim in animations:
        print(anim)
    print(footer)

