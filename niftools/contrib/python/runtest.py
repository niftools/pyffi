from NifFormat.NifFormat import NifFormat
nif = NifFormat()

print "Supported versions:"
for vstr, vnum in nif.versions.items():
    print "%10s 0x%08X"%(vstr, vnum)

print "Default NiNode block"
blk = nif.NiNode()
print blk
