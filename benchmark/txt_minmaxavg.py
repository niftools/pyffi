"""Parse all text files, assumed to contain numbers, and print summary info."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, Python File Format Interface
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

from __future__ import print_function

import argparse
import os
import sys

from summary import confint

parser = argparse.ArgumentParser(
    description='Summary statistics about population mean from sample data.')
parser.add_argument(
    '--robust', dest='robust', default=False, action='store_true',
    help='use median and iqr instead of mean and standard deviation',
    )
parser.add_argument(
    'folder', type=str, action='store',
    help='the folder to process files from',
    )

args = parser.parse_args()

total = {}
folder = sys.argv[1]
for root, dirs, files in os.walk(folder):
    for name in files:
        if not name.endswith(".txt"):
            continue
        print("parsing {0}".format(name))
        total[name] = []
        with open(os.path.join(root, name), "rb") as txtfile:
            for row in txtfile:
                row = row.strip()
                total[name].append(float(row))

def summary(outfile):
    for name, vec in sorted(total.items()):
        low, up = confint(vec, robust=args.robust)
        print("{0:10}: [{1:10.4f}, {2:10.4f}]".format(name, low, up), file=outfile)

summary(sys.stdout)
