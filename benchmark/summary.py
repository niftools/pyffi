"""Some functions to calculate summary info."""

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

import os
import sys

def mean(vec):
    """Sample mean.

    >>> mean([1, 2, 3, 4, 5])
    3.0
    """

    return float(sum(vec)) / len(vec)

def sd(vec):
    """Sample standard deviation.

    >>> sd([1, 2, 3, 4, 5]) # doctest: +ELLIPSIS
    1.581138...
    """
    m = mean(vec)
    return (float(sum((v - m) ** 2 for v in vec)) / (len(vec) - 1)) ** 0.5

def median(vec):
    """
    >>> median([1, 2, 3, 4, 5])
    3
    >>> median([1, 1.5, 4, 5])
    2.75
    >>> median([2, 2, 3, 4, 14])
    3
    """
    vec = sorted(vec)
    mid = (len(vec) - 1) // 2
    if len(vec) & 1:
        return vec[mid]
    else:
        return 0.5 * (vec[mid] + vec[mid + 1])

def mad(vec):
    """Median absolute deviation.

    >>> mad([2, 2, 3, 4, 14])
    1
    """
    m = median(vec)
    return median(abs(x - m) for x in vec)

def iqr(vec):
    """Interquartile range.

    >>> iqr([88, 8, 53, 93, 70, 9, 87, 23, 29, 45])
    64
    >>> iqr([89, 48, 62, 32, 10, 84, 42, 54, 9])
    30
    """
    vec = sorted(vec)
    mid = (len(vec) - 1) // 2
    if len(vec) & 1:
        left = vec[:mid + 1]
        right = vec[mid:]
    else:
        left = vec[:mid + 1]
        right = vec[mid + 1:]
    return median(right) - median(left)

def confint(vec, robust=False):
    """Confidence interval for the population mean at 5% significance."""
    if not robust:
        center = mean(vec)
        bound = 1.96 * sd(vec) / (len(vec) ** 0.5)
    else:
        center = median(vec)
        bound = 1.96 * 1.349 * iqr(vec) / (len(vec) ** 0.5)
    return center - bound, center + bound

if __name__ == "__main__":
    import doctest
    doctest.testmod()
