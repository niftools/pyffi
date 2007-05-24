Installation
------------

Make sure you have pynif installed (see http://niftools.sourceforge.net).

Then, copy makehsl.py to your Hex Workshop structures folder

  C:\Program Files\BreakPoint Software\Hex Workshop 4.2\Structures

and run it. This will create a .hsl file per nif version.

Known issues
------------

Hex Workshop libraries cannot properly deal with conditionals, so
for serious hacking you probably want to edit the .hsl library as you
go, commenting out the parts which are not present in the particular
block you are investigating.