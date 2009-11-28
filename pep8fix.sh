#!/bin/sh

# quick shell script to update code for the new pep8 conventions
# warning: this script is pretty dumb, and you should check the fixes manually
# afterwards

find . -name "*.py" -not -wholename "*git*" -exec perl -pi -w -e 's/versionString/version_string/g' {} \;
find . -name "*.py" -not -wholename "*git*" -exec perl -pi -w -e 's/addChild/add_child/g' {} \;
find . -name "*.py" -not -wholename "*git*" -exec perl -pi -w -e 's/updateCenterRadius/update_center_radius/g' {} \;
find . -name "*.py" -not -wholename "*git*" -exec perl -pi -w -e 's/updateTangentSpace/update_tangent_space/g' {} \;
