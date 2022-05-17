blender_node_tools
==================

A python function module to aid in manipulating node connections
in Blender.

The goal is to make it simpler when adding / removing links between
nodes of a NodeTree. Using the Blender Python API as it exists,
adding links looks something like::

    node_tree.links.new(
        node_tree.nodes['From Node'].outputs['Output'],
        node_tree.nodes['To Node'].inputs['Input']
        )

Now this can look like::

    link_nodes(node_tree, 'From Node:Output', 'To Node:Input')

Even simpler if the input and outputs have only one matching type:::

    link_nodes(node_tree, 'From Node', 'To Node')

When linking nodes, if a node string resolves to multiple sockets,
``link_nodes`` will attempt to link each of them, in order until it
matches with one of the input sockets with the same type.
The only time sockets of different types are connected is when both
input and output resolve to a single socket.

As another example, and even more roundabout in Blender
is the removal of links::

    for link in node_tree.links:
        if link.to_node == node_tree.nodes['Node'] \
            or link.from_node == node_tree.nodes['Node']:
            node_tree.links.remove(link)

Now::

    remove_links(node_tree, 'Node')

Or to remove all inputs::

    remove_links(node_tree, '+Node')

Or just outputs::

    remove_links(node_tree, '-Node')

Syntax
------

``blender_node_tools`` uses a custom string format as a shorthand
to access ``Node``s and ``NodeSocket``s in a Blender ``NodeTree``.

At a baseline, a string represents a Node name.::

    "DemoNode"

On its own, this refers to all sockets of the node.
Depending on the context, input or output sockets can be inferred.
To specify only inputs or only outputs, a leading ``+`` (Inputs)
or `-` (Outputs) can be used.::

    "+DemoNode"

Finally, to refer to a specific socket, the socket name can be placed
after the node name delimited by a ``:``::

    "+DemoNode:DemoSocket"

    "-DemoNode:DemoSocket"

And if the socket name is unique to either side, the leading
input/output specifier is unneeded::

    "DemoNode:DemoOutputSocket"

Something like a compositor mix node may have two inputs of the same
name (e.g. "Image").
These may be targeted with array index notation::

    link_nodes(node_tree, "Image Texture", "Mix:Image[0]")
    link_nodes(node_tree, "Fade Texture",  "Mix:Image[1]")

Functions
---------

``NodeType = Union[str, Node, NodeSocket]``

Data Access:

``get_node(tree: NodeTree, of: NodeType) -> Node``

``get_sockets(tree: NodeTree, node: NodeType) -> List[NodeSocket]``

``get_links(tree: NodeTree, node: NodeType) -> List[NodeLink]``

There are also singular ``get_socket`` and ``get_link`` functions.

``get_subtree(tree: NodeTree, node: NodeType) -> Optional[NodeTree]``

``is_group(node: Node) -> bool``

Graph modification:

``link_nodes(tree: NodeTree, node_from: NodeType, node_to: NodeType, preserve_existing: bool = False) -> int``

``remove_links(tree: NodeTree, node: NodeType, node2: Optional[NodeType] = None) -> int``

If you already have the exact ``NodeLink``, use ``node_tree.links.remove(link)``.

Requirements
------------

Python version 3.6 or later.
Tested with Blender version 2.92, 2.93, and 3.1, will likely work for previous
versions.