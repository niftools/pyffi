#!/usr/bin/python

"""A tool to create binary patches between folders recursively."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2011, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import os
import os.path
from argparse import ArgumentParser
import subprocess

# configuration options

parser = ArgumentParser(description=__doc__)
parser.add_argument('patch_cmd', type=str, help="The patch command.")
parser.add_argument('in_folder', type=str, help="Folder with original files.")
parser.add_argument('out_folder', type=str, help="Folder with updated files.")
parser.add_argument('patches_folder', type=str, help="Folder where patches will be written to.")
args = parser.parse_args()

# actual script

def make_patch(in_file, out_file, patch_file):
    # out_file must exist by construction of the script
    if not os.path.exists(out_file):
        raise RuntimeError("out_file %s not found; bug?")
    # check that in_file exists as well
    if not os.path.exists(in_file):
        print("skipped %s (no original)" % out_file)
        return
    folder = os.path.split(patch_file)[0]
    if not os.path.exists(folder):
        os.mkdir(folder)
    command = [args.patch_cmd, in_file, out_file, patch_file]
    print("making %s" % patch_file)
    subprocess.call(command)

for dirpath, dirnames, filenames in os.walk(args.out_folder):
    for filename in filenames:
        out_file = os.path.join(dirpath, filename)
        in_file = out_file.replace(args.out_folder, args.in_folder, 1)
        patch_file = out_file.replace(args.out_folder, args.patches_folder) + ".patch"
        make_patch(in_file, out_file, patch_file)
