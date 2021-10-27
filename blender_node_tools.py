# ©2021 Dustin Walde
# Licensed under GPL-3.0

import sys

from typing import (
    Tuple,
    List,
    Optional,
    Union,
    )

# compatability shim
if sys.version_info.minor < 8:
    def get_origin(item):
        return item.__origin__

    def get_args(item):
        return item.__args__
else:
    from typing import get_args, get_origin

from bpy.types import (
    CompositorNodeGroup,
    CompositorNodeCustomGroup,
    GeometryNodeGroup,
    Node,
    NodeCustomGroup,
    NodeGroup,
    NodeInputs,
    NodeLink,
    NodeOutputs,
    NodeSocket,
    NodeTree,
    ShaderNodeGroup,
    ShaderNodeCustomGroup,
    TextureNodeGroup,
    )

NodeGroupType = Union[
    CompositorNodeGroup,
    CompositorNodeCustomGroup,
    GeometryNodeGroup,
    NodeCustomGroup,
    NodeGroup,
    ShaderNodeGroup,
    ShaderNodeCustomGroup,
    TextureNodeGroup,
    ] # all have a #node_tree property and are Nodes
NodeType = Union[str, Node, NodeSocket]

INPUT_SYMBOL = '+'
OUTPUT_SYMBOL = '-'
SOCKET_DELIMETER = ':'
PATH_DELIMETER = '/'

def is_group(node: Node) -> bool:
    """
    Check if node is a *GroupNode of some sort
    """
    return _is_union_instance(node, NodeGroupType)

def build_path(*nodes: str,
    input: Union[bool,str]=False,
    output: Union[bool,str]=False) \
        -> str:
    if input != False and output != False:
        raise ValueError("Path cannot be both input and output")

    node_path = PATH_DELIMETER.join(nodes)

    def _format_socket_path(socket, symbol):
        if isinstance(socket, str):
            return '{}{}{}{}'.format(
                symbol, node_path, SOCKET_DELIMETER, socket)

        return '{}{}'.format(symbol, node_path)

    if input != False:
        return _format_socket_path(input, INPUT_SYMBOL)
    elif output != False:
        return _format_socket_path(output, OUTPUT_SYMBOL)

    return node_path

def link_nodes(
    tree: NodeTree,
    link_from: NodeType,
    link_to: NodeType,
    preserve_existing: bool = False) \
        -> int:
    """
    Link from output node to input node.
    If no sockets are specified, this will match as many as it can find.
    Will not create new links to input sockets if preserve_existing is
    set.
    """
    connections = 0

    output_sockets = []
    input_sockets = []

    parent_tree = tree

    if isinstance(link_from, NodeSocket):
        if link_from.is_output:
            output_sockets.append(link_from)
    elif isinstance(link_from, Node):
        for output in link_from.outputs:
            output_sockets.append(output)
    else:
        parent_tree, _, _, output_sockets = resolve_path(tree, link_from)

    if isinstance(link_to, NodeSocket):
        if not link_to.is_output:
            input_sockets.append(link_to)
    elif isinstance(link_to, Node):
        for input in link_to.inputs:
            input_sockets.append(input)
    else:
        parent_tree, _, input_sockets, _ = resolve_path(tree, link_to)

    for i in range(len(input_sockets)):
        input_sockets[i] = [
            input_sockets[i],
            preserve_existing and len(input_sockets[i].links) > 0]

    for output in output_sockets:
        for input_data in input_sockets:
            input, matched = input_data
            if matched:
                continue

            if output.type == input.type \
                or (len(output_sockets) == 1 and len(input_sockets) == 1):
                parent_tree.links.new(output, input)
                input_data[1] = True
                connections += 1
                break

    return connections

def get_link(tree: NodeTree, of: NodeType) -> Optional[NodeLink]:
    links = get_links(tree, of)
    if len(links) == 0:
        return None
    return links[0]

def get_links(tree: NodeTree, of: NodeType) -> List[NodeLink]:
    links = []
    if isinstance(of, NodeSocket):
        links = of.links
    elif isinstance(of, Node):
        for input in of.inputs:
            links.extend(input.links)
        for output in of.outputs:
            links.extend(output.links)
    else:
        _, _, inputs, outputs = resolve_path(tree, of)
        for input in inputs:
            links.extend(input.links)
        for output in outputs:
            links.extend(output.links)

    return links

def remove_links(tree: NodeTree, node: NodeType) -> int:
    removed = 0
    if isinstance(node, str):
        node_tree, node, inputs, outputs = resolve_path(tree, node)
        for input in inputs:
            for link in input.links:
                node_tree.links.remove(link)
                removed += 1
        for output in outputs:
            for link in output.links:
                node_tree.links.remove(link)
                removed += 1
    else:
        for link in get_links(tree, node):
            tree.links.remove(link)
            removed += 1

    return removed

def get_socket(tree: NodeTree, node_path: str) -> NodeSocket:
    return get_sockets(tree, node_path)[0]

def get_sockets(tree: NodeTree, node_path: str) -> List[NodeSocket]:
    _, _, inputs, outputs = resolve_path(tree, node_path)
    inputs.extend(outputs)
    return inputs

def get_tree(tree: NodeTree, node_path: str) -> NodeTree:
    return resolve_path(tree, node_path)[0]

def get_node(tree: NodeTree, node_path: str) -> Node:
    """
    Retrieve the the Node from tree at the given node_path.

    raises ValueError if node_path is invalid.
    """
    return resolve_path(tree, node_path)[1]

def resolve_path(tree: NodeTree, node_path: str) \
    -> Tuple[NodeTree, Node, List[NodeSocket], List[NodeSocket]]:

    path_parts, socket_name, socket_index, include_inputs, include_outputs = \
        _parse_path(node_path)

    current_tree = tree
    for node in path_parts[:-1]:
        if node not in current_tree.nodes:
            _invalid_path(node_path,
                "Node name ({}) not found".format(node))

        current_tree = current_tree.nodes[node]

        if not is_group(current_tree):
            _invalid_path(node_path,
                "Parent node ({}) is not a group.".format(node))

        current_tree = current_tree.node_tree

    leaf_node = path_parts[-1]

    if leaf_node not in current_tree.nodes:
        _invalid_path(node_path,
            "Node name ({}) not found".format(leaf_node))

    node = current_tree.nodes[leaf_node]

    inputs = []
    outputs = []

    def _append_matching_sockets(
        include: bool,
        node_sockets: Union[NodeInputs,NodeOutputs],
        out_sockets: List[NodeSocket]):
        name_count = 0
        if include:
            for socket in node_sockets:
                if socket_name is None or socket_name == socket.name:
                    if socket_index < 0 or socket_index == name_count:
                        out_sockets.append(socket)
                    name_count += 1

    _append_matching_sockets(include_inputs, node.inputs, inputs)
    _append_matching_sockets(include_outputs, node.outputs, outputs)

    return (current_tree, node, inputs, outputs)

# helpers ↓

def _invalid_path(node_path, message):
    raise ValueError("Invalid Path: {}\n{}".format(node_path, message))

def _is_union_instance(item, union_type) -> bool:
    if not get_origin(union_type) is Union:
        raise TypeError("Expected Union type")

    return isinstance(item, get_args(union_type))

def _parse_path(node_path: str) -> Tuple[List[str], str, int, bool, bool]:
    input = True
    output = True
    socket = None
    socket_index = -1
    path_parts = None

    if node_path[0] == INPUT_SYMBOL:
        output = False
        node_path = node_path[1:]
    elif node_path[0] == OUTPUT_SYMBOL:
        input = False
        node_path = node_path[1:]

    parts = node_path.split(SOCKET_DELIMETER)
    if len(parts) > 1:
        socket = parts[-1]
        path_parts = SOCKET_DELIMETER.join(parts[:-1])\
            .split(PATH_DELIMETER)
    else:
        path_parts = node_path.split(PATH_DELIMETER)

    if socket is not None:
        left_bracket = socket.find('[')
        right_bracket = socket.find(']')

        if left_bracket >= 0 and right_bracket >= 2:
            socket_index = int(socket[left_bracket+1:right_bracket])
            socket = socket[:left_bracket]

    return (path_parts, socket, socket_index, input, output)