Release 2.0.1 (Jul 22, 2009)
============================

* Added Windows installer for Python 2.6.

* Updated mopper.exe compiled with msvc 2008 sp1 (fixes issue #2802413,
  reported by pacmorrowind).

* Added pdb session to track cicular references and memory leaks (see
  issues #2787602 and #2795837 reported by alexkapi12 and
  xfrancis147).

* Added valgrind script to check memory usage, and to allow keeping
  track of it between releases (see issues #2787602 and #2795837
  reported by alexkapi12 and xfrancis147).

* Removed parenting in xml model from everywhere except Array, and
  using weakrefs to avoid circular references, which helps with
  garbage collection. Performance should now be slightly improved.

* Updates to xml object model expression syntax.

  - Support for field qualifier '.'.

  - Support for addition '+'.

* Updates to Targa format.

  - Support for RLE compressed Targa files (test file contributed by
    Alphax, see issue #2790494).

  - Read Targa footer, if present (test file contributed by Alphax,
    see issue #2790494).

  - Improved interface: header, image, and footer are now global nodes.

* Updates to xsd object model.

  - Classes and attributes for Collada format are now generated (but not
    yet functional).

Release 2.0.0 (May 4, 2009)
===========================

* Windows installer now detects Maya 2008 and Maya 2009, and their 64 bit
  variants, and can install itself into every Maya version that is found.

* Updates to the XML object model (affects CGF, DDS, KFM, NIF, and TGA).

  - Class customizers are taken immediately from the format class, and not
    from separate modules --- all code from customization modules has been
    moved into the main format classes. The result is that parsing is faster
    by about 50 percent.

  - clsFilePath removed, as it is no longer used.

* Updates and fixes for the KFM format.

  - The Data element inherits from Header, and Header includes also all
    animations, so it is more straightforward to edit files.

  - The KFM files open again in QSkope.

* Updates for the CGF format.

  - CHUNK_MAP no longer constructed in Data.__init__ but in a metaclass.

  - Deprecated functions in CgfFormat have been removed.

* Updates for the NIF format.

  - Synced nif.xml with nifskope's xml (includes fixes for Lazeska).

  - Removed deprecated scripts (niftexdump, nifdump, ffvt3rskinpartition,
    nifoptimize).

  - Fixed scaling bug on nifs whose tree has duplicate nodes. Scaling now no
    longer works recursively, unless you use the scaling spell which handles
    the duplication correctly.

* Updated module names to follow pep8 naming conventions: all modules have
  lower case names.

Release 1.2.4 (Apr 21, 2009)
============================

* Documentation is being converted to Sphinx. Currently some parts of the
  documentation are slightly broken with epydoc. Hopefully the migration will
  be complete in a month or so, resolving this issue.

* removed deprecated PyFFI.Spells code:

  - old style spells no longer supported

  - almost all old spells have been converted to the new spell system
    (the few remaining ones will be ported for the next release)

* nif:

  - nif optimizer can be run on folders from the windows context menu
    (right-click on any folder containing nifs and select "Optimize with PyFFI")

  - synced nif.xml with upstream (adds support for Worldshift, bug fixes)

  - using weak references for Ptr type (this aids garbage collection)

  - added fix_strip niftoaster spell which can remove branches selectively
    (feature request #2164309)

  - new getTangentSpace function for NiTriBasedGeom (works for both Oblivion
    and Fallout 3 style tangent spaces)

  - improved mergeSkeletonRoots function (will also merge roots of skins that
    have no bones in common, this helps a lot with Morrowind imports)

  - new sendDetachedGeometriesToNodePosition function and spell (helps a lot
    with Morrowind imports)

* tga:

  - added support for color map and image data in the xml

  - uses the new data model

  - works again in QSkope

* xml object model:

  - added support for multiplication and division operators in expressions

* fixes for unicode support (prepares for py3k)

Release 1.2.3 (Apr 2, 2009)
===========================

* removed reduce() calls (py3k compatibility)

* started converting print calls (py3k compatibility)

* removed relative imports (py3k compatibility)

* removed BSDiff module (not useful, very slow, use external bsdiff instead)

* nif:

  - fixed the update mopp spell for fallout 3 nifs

  - fixed addShape in bhkPackedNiTriStripsShape for fallout 3 nifs

  - niftoaster sends to stdout instead of stderr so output can be captured
    (reported by razorwing)

Release 1.2.2 (Feb 15, 2009)
============================

* cgf format:

  - fixed various regression bugs that prevented qskope to run on cgf files

  - updated to use the new data system

Release 1.2.1 (Feb 2, 2009)
===========================

* nif format:

  - new addIntegerExtraData function for NiObjectNET

Release 1.2.0 (Jan 25, 2009)
============================

* installer directs to Python 2.5.4 if not installed

* using logging module for log messages

* nif format:

  - swapping tangents and binormals in xml; renaming binormals to bitangents
    (see http://www.terathon.com/code/tangent.html)

  - updates for Fallout 3 format

  - updated skin partition algorithm to work for Fallout 3

    + new triangles argument

    + new facemap argument to pre-define partitions (they will be split further
      if needed to meet constraints)

    + sort vertex weight list by weight in skin partitions (except if padbones
      is true; then sorted by bone index, to keep compatibility with ffvt3r)

    + option to maximize bone sharing

  - mopps take material indices into account and compute welding info
    (attempt to fix mopp multi-material issues, does not yet seem to work though)

  - support for niftools bitflags by converting it to a bitstruct on the fly

  - better algorithm for sending bones to bind position, including spells for
    automating this function over a large number of nifs

  - disable fast inverse in bind pos functions to increase numerical precision

  - new algorithm to sync geometry bind poses, along with spell (this fixes
    many issues with Morrowind imports and a few issues with Fallout 3 imports)

  - more doctests for various functions

  - a few more matrix functions (supNorm, substraction)

* dds format:

  - updated to use the FileFormat.Data method (old inconvenient method removed)

* qskope:

  - refactored the tree model

  - all parenting functions are delegated to seperate DetailTree and GlobalTree
    classes

  - the DetailNode and GlobalNode classes only implement the minimal
    functions to calculate the hierarchy, but no longer host the more
    advanced hierarchy functions and data (this will save memory and
    speed up regular use of pyffi outside qskope)

  - EdgeFilter for generic edge type filtering; this is now a
    parameter for every method that needs to list child nodes

Release 1.1.0 (Nov 18, 2008)
============================

* nif format:

  - a large number of functions have moved from the optimizer spell to
    to the main interface, so they can be easily used in other scripts
    without having to import this spell module
    (getInterchangeableTriShape, getInterchangeableTriStrips,
    isInterchangeable)

  - new convenience functions in NiObjectNET, NiAVObject, and NiNode
    (setExtraDatas, setProperties, setEffects, setChildren, etc.)

  - updates for Fallout 3

* niftoaster

  - new fix_addtangentspace spell to add missing tangent space blocks

  - new fix_deltangentspace spell to remove tangent space blocks

  - new fix_texturepath spell to change / into \ and to fix corrupted
    newline characters (which sometimes resulted from older versions of
    nifskope) in NiSourceTexture file paths

  - new fix_clampmaterialalpha spell

  - new fix_detachhavoktristripsdata spell

  - the ffvt3r skin partition spell is now fix_ffvt3rskinpartition

  - new opt_cleanreflists spell

  - new opt_mergeduplicates spell

  - new opt_geometry spell

  - the optimize spell is now simply implemented as a combination of other
    spells

* new internal implementation of bsdiff algorithm

* removed cry dae filter (an improved version of this filter is now
  bundled with ColladaCGF)

* reorganization of file format description code

  - all generic format description specific code has been moved to the
    PyFFI.ObjectModels.FileFormat module

  - all xml/xsd description specific code has been moved to the
    PyFFI.ObjectModels.XML/XSD.FileFormat modules

  - new NifFormat.Data class which now implements all the nif file read and
    write functions

* completely revamped spell system, which makes it much easier to customize
  spells, and also enables more efficient implementations (thanks to tazpn for
  some useful suggestions, see issue #2122196)

  - toaster can call multiple spells at once

  - toaster takes spell classes instead of modules

  - for backwards compatibility, there is a class factory which turns any old
    spell module into a new spell class (the Toaster class will automatically
    convert any modules that it finds in its list of spells, so you do not need
    to be worried about call the factory explicitly)

  - early inspection of the header is possible, to avoid having to read all of
    the file if no blocks of interest are present

  - possibility to prevent the spell to cast itself on particular branches
    (mostly useful to speed up the spell casting process)

  - spells have callbacks for global initialization and finalization of
    data within the toaster

  - possibility to write output to a log file instead of to sys.stdout

  - better messaging system (auto indentation, list nif tree as spell runs)

  - support for spell hierarchies and spell grouping, in parallel or in series
    or any combination of these

* replaced ad hoc class customization with partial classes (still wip
  converting all the classes)

* xml object model expression parser

  - implemented not operator

  - expressions can combine multiple operators (only use this if the result
    is independent of the order in which these operators are applied)

  - new < and > operators

  - support for vercond attribute for Fallout 3

* started on a new object model based on an ANTLR parser of a grammar aimed at
  file format descriptions; this parser will eventually yield a more streamlined,
  more optimized, and more customizable version of the current xml object model
  (this is not yet bundled with the release, initial code is on svn)

Release 1.0.5 (Sep 27, 2008)
============================

* niftoaster optimize

  - fix for materials named skin, envmap2, etc. (issue #2121098)

  - fix for empty source textures in texdesc (issue #2118481)

* niftoaster

  - new spell to disable parallax (issue #2121283)

* toaster

  - new options --diff and --patch to create and apply patches; interal
    patcher uses bsdiff format, but you can also specify an arbitrary
    external diff/patch command via --diff-cmd and --patch-cmd options
    (the external command must take three arguments: oldfile, newfile,
    and patchfile); note that this is still in experimental stage, not ready
    for production use yet

Release 1.0.4 (Sep 18, 2008)
============================

* niftoaster optimize

  - morph data optimization (issue #2116594, fixes "bow" weapons)

Release 1.0.3 (Sep 17, 2008)
============================

* niftoaster optimize

  - detach NiTriStripsData from havok tree when block is
    shared with geometry data (fixes issue #2065018, MiddleWolfRug01.NIF)

  - fix in case merged properties had controllers (issue #2106668)

* fix writing of block order: bhkConstraint entities now always preceed the
  constraint block (this also fixes the "falling sign" issue with the niftoaster
  optimize spell, issue #2068090)

Release 1.0.2 (Sep 15, 2008)
============================

* "negative mass" fix in inertia calculation

Release 1.0.1 (Sep 12, 2008)
============================

* small fix in uninstaller (didn't remove crydaefilter script)

* crydaefilter converts %20 back into spaces (as rc doesn't recognize %20)

* bugfixes for niftoaster optimize spell (pyffi issue #2065018)

Release 1.0.0 (Jul 24, 2008)
============================

* new NSIS installer (this solves various issues with Vista, and also
  allows the documentation to be bundled)

* new filter to prepare collada (.dae) files for CryEngine2 resource compiler

  - wraps scenes into CryExportNodes

  - corrects id/sid naming

  - fixes init_from image paths

  - adds phong and lamber shader sid's

  - enforces material instance symbol to coincide with target

  - sets material names in correct format for material library and
    physicalization

* started on support for collada format, by parsing the collada xsd schema
  description (this is still far from functional, but an initial parser is
  already included with the library, although it does not yet create any
  classes yet)

* fully optimal mopp generation for Oblivion (using the NifTools mopper.exe
  which is a command line utility that calls the mopp functions in the havok
  library, credit for writing the original wrapper goes to tazpn)

* minor updates to the nif.xml format description

* refactoring: library reorganized and some interfaces have been
  unified, also a lot of code duplication has been reduced; see
  README.TXT for more details on how to migrate from 0.x.x to 1.x.x

  - main format classes PyFFI.XXX have been moved to PyFFI.Formats.XXX

  - "XxxFormat.getVersion(cls, stream)" now always returns two
    integers, version and user_version

  - "XxxFormat.read(self, stream, version, user_version, ...)" for all
    formats

  - "XxxFormat.write(self, stream, version, user_version, \*readresult, ...)"
    for all formats

  - in particular, CGF format game argument removed from read and
    write functions, but there are new CgfFormat.getGame and
    CgfFormat.getGameVersion functions to convert between (version,
    user_version) and game

  - also for the CGF format, take care that getVersion no longer
    returns the file type. It is returned with the CgfFormat.read
    function, however there is a new CgfFormat.getFileType function, if
    you need to know the file type but you don't want to parse the whole
    file

  - all XxxFormat classes derive from XmlFileFormat base class

  - common nameAttribute, walk, and walkFile functions

  - XxxTester modules have been moved to PyFFI.Spells.XXX, along with a much
    improved PyFFI.Spells module for toasters with loads of new options

  - some other internal code has been moved around

    + qskopelib -> PyFFI.QSkope
    + PyFFI.Bases -> PyFFI.ObjectModels.XML

  - a lot more internal code reorganization is in progress...

* much documentation has been added and improved

Release 0.11.0 (Jun 16, 2008)
=============================

* nif:

  - fixed updateTangentSpace for nifs with zero normals

* cfg:

  - a lot of new physics stuff: MeshPhysicsDataChunk mostly decoded (finally!!)

  - fixes for reading and writing caf files (they are missing controller
    headers)

  - activated BoneMeshChunk and BoneInitialPosChunk for Crysis

* tga:

  - improved tga file detection heuristic

Release 0.10.10 (Jun 8, 2008)
=============================

* nif:

  - minor updates in xml

  - NiPixelData saveAsDDS function now also writes DXT compressed formats,
    that is, pixel formats 4, 5, and 6 (contributed by taarna23)

  - fixed nifoptimize for nifs with particle systems (niftools issue #1965936)

  - fixed nifoptimize for nifs with invalid normals (niftools issue #1987506)

Release 0.10.9 (May 27, 2008)
=============================

* nif:

  - bspline interpolator fix if no keys

  - fixed bspline scale bug

Release 0.10.8 (Apr 13, 2008)
=============================

* cgf:

  - more decoded of the mesh physics data chunk

* nif:

  - scaling for constraints

  - ported the A -> B spell from nifskope (see the new getTransformAB and
    updateAB methods)

Release 0.10.7 (Apr 5, 2008)
============================

* cgf:

  - indices are unsigned shorts now (fixes geometry corruption on import of
    large models)

  - MeshChunk.setGeometry gives useful error message if number of vertices is
    too large

* nif:

  - nif.xml has minor updates in naming

  - added NiBSplineData access functions (experimental, interface could still
    change)

  - started on support for compressed B-spline data

  - fixed block order writing of bhkConstraints

Release 0.10.6 (Mar 30, 2008)
=============================

* tga: added missing xml file

* nif:

  - removed some question marks so the fields can be accessed easily in python
    interface

  - ControllerLink and StringPalette functions and doctests

  - quaternion functions in Matrix33 and Matrix44

  - new bspline modules (still to implement later)

  - fixed NiTransformInterpolator scaling bug

* cgf:

  - use tempfile for write test

* quick install batch file for windows

Release 0.10.5 (Mar 27, 2008)
=============================

* qskope: make bitstructs editable

* cgf:

  - MeshChunk functions to get vertex colors (game independent).

  - Set vertex colors in setGeometry function.

Release 0.10.4 (Mar 26, 2008)
=============================

* cgf:

  - fixed tangent space doctest

  - setGeometry argument sanity checking

  - setGeometry fix for empty material list

  - setGeometry tangent space update fix if there are no uvs

Release 0.10.3 (Mar 24, 2008)
=============================

* added support for the TGA format

* tangentspace:

  - validate normals before calculating tangents

  - added new option to get orientation of tangent space relative to texture
    space (Crysis needs to know about this)

* installer detects Maya 2008 and copies relevant files to Maya Python
  directory for the Maya scripts to work

* cgf:

  - tangent space cgftoaster

  - new MeshChunk updateTangentSpace function


Release 0.10.2 (Mar 22, 2008)
=============================

* cgf:

  - fixed "normals" problem by setting last component of tangents to -1.0

  - meshchunk function to get all material indices, per triangle (game
    independent)

  - scaling fixes for datastreamchunk, meshchunk, and meshsubsetschunk

  - fixed version of BreakablePhysicsChunk

  - a few new findings in decoding the physics data (position and rotation)

Release 0.10.1 (Mar 21, 2008)
=============================

* cgf:

  - some minor xml updates

  - setGeometry function for MeshChunk to set geometry for both Far Cry and
    Crysis in a unified way

  - uv.v opengl flip fix for Crysis MeshChunk data

* MathUtils: new function to calculate bounding box, center, and radius

* qskope: fixed bug which prevented setting material physics type to NONE

Release 0.10.0 (Mar 8, 2008)
============================

* cgf: ported A LOT of stuff from the Crysis Mod SDK 1.2; the most common
  CE2 chunks now read and write successfully

Release 0.9.3 (Mar 7, 2008)
===========================

* cgf:

  - decoded a lot of geometry data

    + vertices
    + normals
    + vertex colors
    + uvs
    + mesh material info

  - started decoding many other chunk types

  - added chr chunk types so files containing them can be processed (the data
    is ignored)

  - started adding functions to MeshChunk to have unified access to geometry
    data for both Far Cry and Crysis cgf files

* windows installer registers chr extension with qskope

Release 0.9.2 (Feb 26, 2008)
============================

* full support for the xml enum tag type, with improved editor in qskope

* new common string types (shared between cgf and nif formats)

  - null terminated

  - fixed sized

  - variable sized starting with integer describing length

* qskope: no more duplicate ptr refs in global view

* qskope: refactored delegate editor system to be more transparent and much
  easier to extend

* cgf: crysis chunks have been partially decoded (still very much wip)

* cgf: added extra chunk size check on read to aid decoding

* dds: register dds extension with qskope on windows install

* nif: nifoptimize clamps material alpha to [0,1]

Release 0.9.1 (Feb 22, 2008)
============================

* full support for the xml bitstruct tag (for types that contain bit flags)

* added PyFFI.Formats.DDS library for dds file format

* nif: new function for NiPixelData to save image as dds file

* niftoaster: script for exporting images from NiPixelData blocks

* nifoptimize:

  - merge identical shape data blocks

  - remove empty NiNode children

  - update skin partition only if block already exists

Release 0.9.0 (Feb 11, 2008)
============================

* added PyFFI.Formats.KFM library for kfm file format

* cgf.xml and nif.xml updates

* new qBlockParent function to assign parents if the parent block does not
  contain a reference to the child, but the child contains a reference to the
  parent (as in MeshMorphTargetChunk and BoneInitialPosChunk)

* QSkope: root blocks sorted by reference number

* QSkope: added kfm format

* niftexdump: bug fixed when reading nifs that have textures without source

Release 0.8.2 (Jan 28, 2008)
============================

* fixed installer bug (nifoptimize would not launch from context menu)

* qskope:

  - handle back-references and shared blocks

  - blocks are now numbered

  - improved display references


Release 0.8.1 (Jan 27, 2008)
============================

* deep copy for structs and arrays

* nifoptimize:

  - detects cases where triangulated geometry performs better than stripified
    geometry (fixes a performance issue with non-smooth geometry reported by
    Lazarus)

  - can now also optimize NiTriShapes

  - throws away empty and/or duplicate children in NiNode lists

Release 0.8.0 (Jan 27, 2008)
============================

* qskope: new general purpose tool for visualizing files loaded with PyFFI

* cgf: corrected the bool implementation (using True/False rather than an int)

* nif: many xml updates, support for Culpa Innata, updates for emerge demo

* support for forward declaration of types (required for UnionBV)

* PyFFI.__hexversion__ for numeric represenation of the version number

Release 0.7.5 (Jan 14, 2008)
============================

* added a DTD for the 'fileformat' document type, to validate the xml

* bits tag for bitstructs, instead of add tag, to allow validation

* cgf: write the chunk header table at start, for crysis

* nifoptimize:

  - new command line option '-x' to exclude blocks per type

  - fixes corrupted texture paths (that is, files that got corrupted with
    nifskope 1.0 due to the \\r \\n bug)

  - on windows, the script can now be called from the .nif context menu

  - accept both lower and upper case 'y' for confirmation

  - new command line option '-p' to pause after run

* niftoaster: fix reporting of file size difference in readwrite test

* bug fixed when writing nifs of version <= 3.1

* support for multiple 'Top Level Object' (roots) for nifs of version <= 3.1

* various xml fixes

  - new version 20.3.0.2 from emerge demo

  - NiMeshPSysData bugfix and simplification

  - replaced NiTimeController Target with unknown int to cope with invalid
    pointers in nif versions <= 3.1

* fixed bug nifmakehsl.py script

* fixed bug in nifdump.py script

* new post installation script for installing/uninstalling registry keys

Release 0.7.4 (Dec 26, 2007)
============================

* fix in nif xml for a long outstanding issue which caused some nifs with mopp
  shapes to fail

* fixed file size check bug in readwrite test for nif and cgf

* initial read and write support for crysis cgf files

* support for versions in structs

* updates for controller key types 6, 9, and 10, in cgf xml

Release 0.7.3 (Dec 13, 2007)
============================

* nif: fixed error message when encountering empty block type

* nif: dump script with block selection feature

* cgf: fix transform errors, ported matrix and vector operations from nif
  library

Release 0.7.2 (Dec 3, 2007)
===========================

* NifTester: new raisereaderror argument which simplifies the older system and
  yields more instructive backtraces

* nif: better support for recent nif versions, if block sizes do not match
  with the number of bytes read then the bytes are skipped and a warning is
  printed, instead of raising an exception

Release 0.7.1 (Nov 27, 2007)
============================

* nif: fixed applyScale in bhkRigidBody

Release 0.7 (Nov 19, 2007)
==========================

* fixed a problem locating the customized functions for Fedora 8 python which 
  does not look in default locations besides sys.path

* new vector and matrix library under Utils (for internal use)

* new quick hull library for computing convex hulls

* new inertia library for computing mass, center of gravity, and inertia
  tensors of solid and hollow objects

* nif: fixed order of bhkCollisionObject when writing nif files

* nif: new bhkRigidBody function for updating inertia, center of gravity, and
  mass, for all types of primitives

Release 0.6 (Nov 3, 2007)
=========================

* nifoptimize removes duplicate property blocks

* reduced memory footprint in skin data center and radius calculation for the
  nif format

* new option to ignore strings when calculating hash

* code has been cleaned up using pylint

* added a lot more documentation

* refactored all common functions to take \*\*kwargs as argument

* read and write functions have the file stream as first non-keyword argument

* refactored and simplified attribute parsing, using a common
  _filteredAttributeList method used by all methods that need to parse
  attributes; the version and user_version checks are now also consistent over
  all functions (i.e. getRefs, getLinks, etc.)

* added more doctests

Release 0.5.2 (Oct 25, 2007)
============================

* added hash functions (useful for identifying and comparing objects)

Release 0.5.1 (Oct 19, 2007)
============================

* fixed a bug in the nif.xml file which prevented Oblivion skeleton.nif files
  to load

Release 0.5 (Oct 19, 2007)
==========================

* new functions to get block size

* various small bugs fixed

* nif: support for new versions (20.2.0.6, 20.2.0.7, 20.2.0.8, 20.3.0.3,
  20.3.0.6, 20.3.0.9)

* nif: block sizes are now also written to the nif files, improving support
  for writing 20.2.0.7+ nif versions

* nif: fixed flattenSkin bug (reported by Kikai)

Release 0.4.9 (Oct 13, 2007)
============================

* nif: nifoptimize no longer raises an exception on test errors, unless you
  pass the -r option

* nif: nifoptimize will try to restore the original file if something goes 
  wrong during write, so - in theory - it should no longer leave you with 
  corrupt nifs; still it is recommended to keep your backups around just in case

* nif: niftesters recoded to accept arbitrary argument dictionaries; this
  could cause incompatibilities for people writing their own scripts, but the
  upgrade to the new system is fairly simple: check the niftemplate.py script

* nif: fixed bug in updateTangentSpace which caused an exception when uvs or
  normals were not present

* nif: doctest for unsupported blocks in nifs

Release 0.4.8 (Oct 7, 2007)
===========================

* cgf: MeshMorphTargetChunk is now supported too

* nif: new script (niftexdump.py) to dump texture and material info

* nif: added template script for quickly writing new nif scripts

Release 0.4.7 (Oct 4, 2007)
===========================

* nif: new optimizer script

Release 0.4.6 (Sep 29, 2007)
============================

* nif and cgf documentation improved

* added a number of new doctests

* nif: new scripts

  - niftoaster.py for testing and modifying nif files (contributed by wz)

  - nifvisualizer.py for visualizing nif blocks (contributed by wz)

  - nifmakehsl.py for making hex workshop structure libraries for all nif
    versions

* nif: bundling NifVis and NifTester modules so you can make your own nif
  toasters and visualizers

* nif: fixed rare issue with skin partition calculation

* cgf: new script

  - cgftoaster.py for testing and modifying cgf files (similar to niftoaster.py)

* cgf: bundling CgfTester module so you can make your own cgf toasters

* cgf: various xml bugs fixed

* cgf: write support improved (but not entirely functional yet)

* cgf: material chunk custom function for extraction material shader and script

* Expression.py: support for empty string check in condition
	
Release 0.4.5 (Sep 16, 2007)
============================

* issue warning message instead of raising exception for improper rotation
  matrix in setScaleRotationTranslation

* fixed skin partition bug during merge

* skin partition bone index padding and sorting for Freedom Force vs. the 3rd
  Reich

Release 0.4.4 (Sep 2, 2007)
===========================

* added mopp parser and simple mopp generator

Release 0.4.3 (Aug 17, 2007)
============================

* fixed bug that occurred if userver = 0 in the xml (fixes geometry morph data
  in NIF versions 20.0.0.4 and up)

* NIF:

  - tree() function has been extended

  - some minor cleanups and more documentation

Release 0.4.2 (Aug 15, 2007)
============================

* kwargs for getRefs

* NIF:

  - fixed bug in skin partition calculation

  - when writing nif files the refs are written in sequence (instead of the
    links, so missing links will yield an exception, which is a good thing)

  - new functions to get list of extra data blocks and to add effect

Release 0.4.1 (Aug 14, 2007)
============================

* NIF:

  - new function to add collision geometries to packed tristripsshape

  - fixed bug in bhkListShape.addShape

Release 0.4 (Aug 12, 2007)
==========================

* NIF:

  - new function updateBindPosition in NiGeometry to fix a geometry rest
    position from current bone positions

  - removed deprecated functions

  - (!) changed interface of addBone, no longer takes "transform" argument; use
    the new function updateBindPosition instead

Release 0.3.4 (Aug 11, 2007)
============================

* improved documentation

* fixed the 'in' operator in Bases/Array.py

* NIF:

  - doctest for NiNode

  - flatten skin fix for skins that consist of multiple shapes

  - support for the most common oblivion havok blocks

Release 0.3.3 (Aug 8, 2007)
===========================

* NIF:

  - fixed a bug in the skin center and radius calculation

  - added copy function to Vector3

  - fixed NiGeometry doctest

Release 0.3.2 (Aug 7, 2007)
===========================

* simplified interface (still wip) by using keyword arguments for common
  functions such as read and write

* NIF:

  - fix for skin partition blocks in older nif versions such as
    Freedom Force vs. 3rd Reich

  - support for triangle skin partitions

  - added stitchstrips option for skin partitions

  - added a NiGeometry function to send bones to bind pose

Release 0.3.1 (Aug 6, 2007)
===========================

* NIF:

  - new function for getting geometry skin deformation in rest pose

  - old rest pose functions are deprecated and will be removed from a future
    release

Release 0.3 (Aug 2, 2007)
=========================

* NIF:

  - fixed an issue with writing skeleton.nif files

* CGF:

  - reading support for the most common blocks in static cgf files;
    experimental

Release 0.2.1 (Jul 29, 2007)
============================

* NIF:

  - fixed bug in getTransform

  - new option in findChain to fix block type

Release 0.2 (Jul 29, 2007)
==========================

* fixed argument passing when writing arrays

* NIF: added getControllers function to NiObjectNET

Release 0.1 (Jul 22, 2007)
==========================

* bug fixed when writing array of strings

* NIF

  - new function to add bones

  - XML update, supports newer versions from Emerge Demo

Release 0.0 (Jul 7, 2007)
=========================

* first public release
