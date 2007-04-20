def test():
    from NifFormat.NifFormat import NifFormat

# this just parses the xml without doing anything else
# (for comparison)
def test_dom():
    from xml.dom.minidom import parse
    parse("nif.xml")

import profile
profile.run("test()", "profile.txt")
profile.run("test_dom()", "profile_dom.txt")
    
# print slowest functions, sorted by time
# (including time spent in subfunctions)

import pstats

p = pstats.Stats("profile.txt")
p.strip_dirs()
p.sort_stats('cumulative').print_stats('XmlHandler.py:')

p = pstats.Stats("profile_dom.txt")
p.strip_dirs()
p.sort_stats('cumulative').print_stats(10)
