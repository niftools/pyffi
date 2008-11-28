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
L{GlobalDGraph} class implements the global level, which does not show
any actual data, but only structure.

The global level forms a directed graph where the nodes are data
blocks and directed edges represent links from one block to
another. The full graph is implemented in the L{GlobalDGraph}
class.

This directed graph is assumed to have a (not necessarily unique)
spanning tree, that is, a subgraph which contains all nodes of the
original graph, which contains no cycles, and for which each node has
at most one parent. The spanning tree is implemented in the
L{GlobalNode} class.

For some data, a directed acyclic graph, which is not necessarily a
tree (that is, a single node may have multiple parents), may naturally
arise as well. This is implemented in the L{GlobalDAGraph} class.

The L{PyFFI.ObjectModels.FileFormat.Data} class is the root node of the
spanning tree. Recursing over this node will visit each node exactly once,
in a hierarchical order.

The base classes are roughly based on the TreeItem example in the Qt docs:
http://doc.trolltech.com/4.4/itemviews-simpletreemodel.html

@todo: Still a work in progress, classes are not actually used
anywhere yet, and names may still change.
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

class DetailNode(object):
    """A node of the detail tree which can have children.

    If the data must be editable, also derive the class from one of
    the delegate classes defined in L{PyFFI.ObjectModels.Editable},
    and make sure that the getValue and setValue functions are
    implemented.
    """

    def getDetailChildNodes(self):
        """Generator which yields all children of this item in the detail view.

        Override this method if the node has children.

        @return: Generator for detail tree child nodes.
        @rtype: generator yielding L{DetailNode}s
        """
        return (dummy for dummy in ())

    def getDetailChildNames(self):
        """Generator which yields all child names of this item in the detail
        view.

        Override this method if the node has children.

        @return: Generator for detail tree child names.
        @rtype: generator yielding C{str}s
        """
        return (dummy for dummy in ())

    def getDetailDataDisplay(self):
        """Object used to display the instance in the detail view.

        Override this method if the node has data to display in the detail view.

        @return: A string that can be used to display the instance.
        @rtype: C{str}
        """
        return ""

class GlobalNode(DetailNode):
    """A node of the global graph that can also appear fully in the detail
    view.
    """

    def getGlobalNodeType(self):
        """The type of this global branch for display purposes.
        Override this method.

        @return: A string.
        """
        raise NotImplementedError
        # possible implementation:
        #return self.__class__.__name__

    def getGlobalNodeId(self):
        """Unique reference id for this global branch for display
        purposes. Override this method.

        @return: An integer.
        """
        raise NotImplementedError

    def getGlobalNodeDataDisplay(self):
        """Very short summary of the data of this global branch for display
        purposes. Override this method.

        @return: A string.
        """
        raise NotImplementedError
        # possible implementation:
        #return self.name if hasattr(self, "name") else ""

    def getGlobalNodeParent(self):
        """Return parent of the spanning tree. Override this method.

        @return: The in the graph.
        @rtype: L{GlobalNode} or C{NoneType}
        """
        raise NotImplementedError

    def getGlobalNodeChildren(self):
        """Generator which yields all children of this item in the global view.
        Override this method.

        @return: Generator for global tree children.
        """
        raise NotImplementedError

    def getGlobalNodeNumChildren(self):
        """Return number of children of this item in the global view.
        Override this method.

        @return: Number of global children as int.
        """
        raise NotImplementedError

    def getGlobalNodeChild(self, row):
        """Find row'th child for global view. Override this method.

        @param row: The row number.
        @type row: int
        @return: The child (must be a L{GlobalNode}).
        """
        raise NotImplementedError

    def getGlobalNodeChildRow(self, item):
        """Find the row number of the given child for global view.
        Override this method.

        @param item: The child.
        @type item: any
        @return: The row, as int.
        """
        raise NotImplementedError

    def replaceGlobalNode(self, oldbranch, newbranch):
        """Replace a particular branch in the tree/graph."""
        raise NotImplementedError

    def getGlobalNodeIterator(self):
        """Iterate over self, all children, all grandchildren, and so on.
        Do not override.
        """
        yield self
        for child in self.getGlobalNodeChildren():
            for branch in child.getGlobalNodeIterator():
                yield branch

    def updateGlobalNode(self):
        """Recalculate spanning tree."""
        raise NotImplementedError

