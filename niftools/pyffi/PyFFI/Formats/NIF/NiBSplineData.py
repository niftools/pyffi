"""Custom functions for NiBSplineData.

>>> # a doctest
>>> from PyFFI.Formats.NIF import NifFormat
>>> block = NifFormat.NiBSplineData()
>>> block.numShortControlPoints = 50
>>> block.shortControlPoints.updateSize()
>>> for i in xrange(block.numShortControlPoints):
...     block.shortControlPoints[i] = 20 - i
>>> list(block.getShortData(12, 4, 3))
[(8, 7, 6), (5, 4, 3), (2, 1, 0), (-1, -2, -3)]
>>> offset = block.appendShortData([(1,2),(4,3),(13,14),(8,2),(33,33)])
>>> offset
50
>>> list(block.getShortData(offset, 5, 2))
[(1, 2), (4, 3), (13, 14), (8, 2), (33, 33)]
>>> list(block.getCompData(offset, 5, 2, 10.0, 32767.0))
[(11.0, 12.0), (14.0, 13.0), (23.0, 24.0), (18.0, 12.0), (43.0, 43.0)]
>>> block.appendFloatData([(1.0,2.0),(3.0,4.0),(0.5,0.25)])
0
>>> list(block.getFloatData(0, 3, 2))
[(1.0, 2.0), (3.0, 4.0), (0.5, 0.25)]
>>> block.appendCompData([(1,2),(4,3)])
(60, 2.5, 1.5)
>>> list(block.getShortData(60, 2, 2))
[(-32767, -10922), (32767, 10922)]
>>> list(block.getCompData(60, 2, 2, 2.5, 1.5)) # doctest: +ELLIPSIS
[(1.0, 2.00...), (4.0, 2.99...)]
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, NIF File Format Library and Tools.
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
#    * Neither the name of the NIF File Format Library and Tools
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

def _getData(self, offset, num_elements, element_size, controlpoints):
    """Helper function for getFloatData and getShortData. For internal
    use only."""
    # check arguments
    if not (controlpoints is self.floatControlPoints
            or controlpoints is self.shortControlPoints):
        raise ValueError("internal error while appending data")
    # parse the data
    for element in xrange(num_elements):
        yield tuple(
            controlpoints[offset + element * element_size + index]
            for index in xrange(element_size))

def _appendData(self, data, controlpoints):
    """Helper function for appendFloatData and appendShortData. For internal
    use only."""
    # get number of elements
    num_elements = len(data)
    # empty list, do nothing
    if num_elements == 0:
        return
    # get element size
    element_size = len(data[0])
    # store offset at which we append the data
    if controlpoints is self.floatControlPoints:
        offset = self.numFloatControlPoints
        self.numFloatControlPoints += num_elements * element_size
    elif controlpoints is self.shortControlPoints:
        offset = self.numShortControlPoints
        self.numShortControlPoints += num_elements * element_size
    else:
        raise ValueError("internal error while appending data")
    # update size
    controlpoints.updateSize()
    # store the data
    for element, datum in enumerate(data):
        for index, value in enumerate(datum):
            controlpoints[offset + element * element_size + index] = value
    # return the offset
    return offset

def getShortData(self, offset, num_elements, element_size):
    """Get an iterator to the data.

    @param offset: The offset in the data where to start.
    @param num_elements: Number of elements to get.
    @param element_size: Size of a single element.
    @return: A list of C{num_elements} tuples of size C{element_size}.
    """
    return self._getData(
        offset, num_elements, element_size, self.shortControlPoints)

def getCompData(self, offset, num_elements, element_size, bias, multiplier):
    """Get an interator to the data, converted to float with extra bias and
    multiplication factor. If C{x} is the short value, then the returned value
    is C{bias + x * multiplier / 32767.0}.

    @param offset: The offset in the data where to start.
    @param num_elements: Number of elements to get.
    @param element_size: Size of a single element.
    @param bias: Value bias.
    @param multiplier: Value multiplier.
    @return: A list of C{num_elements} tuples of size C{element_size}.
    """
    for key in self.getShortData(offset, num_elements, element_size):
        yield tuple(bias + x * multiplier / 32767.0 for x in key)

def appendShortData(self, data):
    """Append data.

    @param data: A list of elements, where each element is a tuple of
        integers. (Note: cannot be an interator; maybe this restriction
        will be removed in a future version.)
    @return: The offset at which the data was appended."""
    return self._appendData(data, self.shortControlPoints)

def appendCompData(self, data):
    """Append data as compressed list.

    @param data: A list of elements, where each element is a tuple of
        integers. (Note: cannot be an interator; maybe this restriction
        will be removed in a future version.)
    @return: The offset, bias, and multiplier."""
    # get extremes
    maxvalue = max(max(datum) for datum in data)
    minvalue = min(min(datum) for datum in data)
    # get bias and multiplier
    bias = 0.5 * (maxvalue + minvalue)
    if maxvalue > minvalue:
        multiplier = 0.5 * (maxvalue - minvalue)
    else:
        # no need to compress in this case
        multiplier = 1.0

    # compress points into shorts
    shortdata = []
    for datum in data:
        shortdata.append(tuple(int(32767 * (x - bias) / multiplier)
                               for x in datum))
    return (self._appendData(shortdata, self.shortControlPoints),
            bias, multiplier)

def getFloatData(self, offset, num_elements, element_size):
    """Get an iterator to the data.

    @param offset: The offset in the data where to start.
    @param num_elements: Number of elements to get.
    @param element_size: Size of a single element.
    @return: A list of C{num_elements} tuples of size C{element_size}.
    """
    return self._getData(
        offset, num_elements, element_size, self.floatControlPoints)

def appendFloatData(self, data):
    """Append data.

    @param data: A list of elements, where each element is a tuple of
        floats. (Note: cannot be an interator; maybe this restriction
        will be removed in a future version.)
    @return: The offset at which the data was appended."""
    return self._appendData(data, self.floatControlPoints)

if __name__=='__main__':
    import doctest
    doctest.testmod()
