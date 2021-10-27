blender_node_tools
==================

A python function module to aid in manipulating node connections
in Blender.

The goal is to make it simpler when adding / removing links between
nodes of a NodeTree. Using the Blender Python API, adding links looks
something like::

    node_tree.links.new(
        node_tree.nodes['From Node'].outputs['Output'],
        node_tree.nodes['To Node'].inputs['Input']
        )

Now this can look like::

    link_nodes(node_tree, 'From Node', 'To Node:Input')

Even more roundabout was the removal of links::

    for link in node_tree.links:
        if link.to_node == node_tree.nodes['Node'] \
            or link.from_node == node_tree.nodes['Node']:
            node_tree.links.remove(link)

Now::

    remove_links(node_tree, 'Node')

Or to remove all inputs::

    remove_links(node_tree, '+Node')

Outputs::

    remove_links(node_tree, '-Node')


Something like a compositor mix node have two inputs of the same name
"Image". These may be targeting with array index notation::

    link_nodes(node_tree, "Image Texture", "Mix:Image[0]")
    link_nodes(node_tree, "Fade Texture",  "Mix:Image[1]")

Requirements
------------

Python version 3.6 or later.
Tested with Blender version 2.92, will likely work for previous
versions.