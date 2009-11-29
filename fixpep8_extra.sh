#!/bin/sh

find . -not -wholename "*git*" -exec perl -pi -w -e 's/getValue/get_value/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/setValue/set_value/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/IsInterchangeable/is_interchangeable/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getHash/get_hash/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getSize/get_size/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/fixLinks/fix_links/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getStrings/get_strings/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/hasStrings/has_strings/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/hasLinks/has_links/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getLinks/get_links/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getRefs/get_refs/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/hasRefs/has_refs/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/replaceGlobalNode/replace_global_node/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getDetailDisplay/get_detail_display/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getGlobalDisplay/get_global_display/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getEditorValue/get_editor_value/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/setEditorValue/set_editor_value/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getDetailChildNodes/get_detail_child_nodes/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getGlobalChildNodes/get_global_child_nodes/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getDetailChildNames/get_detail_child_names/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/get_mass_center_inertiaPolyhedron/get_mass_center_inertia_polyhedron/g' {} \;
find . -not -wholename "*git*" -exec perl -pi -w -e 's/getMassCenterInertiaPolyhedron/get_mass_center_inertia_polyhedron/g' {} \;

