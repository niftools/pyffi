"""Base classes for organizing data (for instance to visualize data
with Qt, or to run hierarchical checks) in a global graph, and a
detail tree at each node of the global graph.

The classes defined here assume that data can be organized in two
stages: a global level which only shows 'top-level' objects
(i.e. large file blocks, chunks, and so on) as nodes and links between
the nodes via directed arcs, and a detail level which shows the
details of a top-level object, that is, the actual data they
contain.

L{DetailNode} implements the detail side of things. The
L{GlobalNode} class implements the global level, which does not show
any actual data, but only structure.

The global level forms a directed graph where the nodes are data
blocks and directed edges represent links from one block to
another.

This directed graph is assumed to have a spanning acyclic directed
graph, that is, a subgraph which contains all nodes of the original
graph, and which contains no cycles. This graph constitutes of those
edges which have edge type zero.

The L{PyFFI.ObjectModels.FileFormat.Data} class is the root node of
the graph. Recursing over all edges of type zero of this node will
visit each node (possibly more than once) in a hierarchical order.

The base classes are roughly based on the TreeItem example in the Qt docs:
http://doc.trolltech.com/4.4/itemviews-simpletreemodel.html
"""

# --------------------------------------------------------------------------
# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2008, Python File Format Interface
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
# --------------------------------------------------------------------------

from itertools import repeat

class DetailNode(object):
    """A node of the detail tree which can have children.

    If the data must be editable, also derive the class from one of
    the delegate classes defined in L{PyFFI.ObjectModels.Editable},
    and make sure that the getValue and setValue functions are
    implemented.
    """

    def getDetailChildNodes(self, edge_type=0):
        """Generator which yields all children of this item in the detail view.

        Override this method if the node has children.

        @return: Generator for detail tree child nodes.
        @rtype: generator yielding L{DetailNode}s
        """
        return (dummy for dummy in ())

    def getDetailChildNames(self, edge_type=0):
        """Generator which yields all child names of this item in the detail
        view.

        Override this method if the node has children.

        @return: Generator for detail tree child names.
        @rtype: generator yielding C{str}s
        """
        return (dummy for dummy in ())

    def getDetailEdgeTypes(self):
        """Generator which yields all edge types of this item in the
        detail view, one edge type for each child.

        Override this method if you rely on non-zero edge types.
        """
        return repeat(0)

    def getDetailDataDisplay(self):
        """Object used to display the instance in the detail view.

        Override this method if the node has data to display in the detail view.

        @return: A string that can be used to display the instance.
        @rtype: C{str}
        """
        return ""

    def getDetailIterator(self, edge_type=0):
        """Iterate over self, all children, all grandchildren, and so
        on (only given edge type is followed). Do not override.
        """
        yield self
        for child in self.getDetailChildNodes(edge_type=edge_type):
            for branch in child.getDetailIterator(edge_type=edge_type):
                yield branch

class GlobalNode(DetailNode):
    """A node of the global graph that can also appear fully in the detail
    view.
    """

    def getGlobalDataDisplay(self):
        """Very short summary of the data of this global branch for display
        purposes. Override this method.

        @return: A string.
        """
        return ""
        # possible implementation:
        #return self.name if hasattr(self, "name") else ""

    def getGlobalChildNodes(self, edge_type=0):
        """Generator which yields all children of this item in the
        global view, of given edge type (default is edges of type 0).

        Override this method.

        @param edge_type: If not C{None}, only children for edges of given
            type are given.
        @type edge_type: C{int} or C{NoneType}

        @return: Generator for global node children.
        """
        return (dummy for dummy in ())

    def getGlobalEdgeTypes(self):
        """Generator which yields all edge types of this item in the
        global view, one edge type for each child.

        Override this method if you rely on non-zero edge types.
        """
        return repeat(0)

    def replaceGlobalNode(self, oldnode, newnode):
        """Replace a particular branch in the graph (only edge_type=0 is
        followed).
        """
        raise NotImplementedError

    def getGlobalIterator(self, edge_type=0):
        """Iterate over self, all children, all grandchildren, and so
        on (only given edge_type is followed). Do not override.
        """
        yield self
        for child in self.getGlobalNodeChildren(edge_type=edge_type):
            for branch in child.getGlobalIterator(edge_type=edge_type):
                yield branch
