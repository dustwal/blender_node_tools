# ©2021-2022 Dustin Walde
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

def is_group(node: Node) -> bool:
    """
    Check if node is a *GroupNode of some sort.
    """
    return _is_union_instance(node, NodeGroupType)

def format_node(node: str,
    input: Union[bool,str]=False,
    output: Union[bool,str]=False) \
        -> str:
    if input != False and output != False:
        raise ValueError("Node ref cannot be both input and output")

    if input != False:
        return _format_socket_str(node, input, INPUT_SYMBOL)
    elif output != False:
        return _format_socket_str(node, output, OUTPUT_SYMBOL)

    return node

def link_nodes(
    tree: NodeTree,
    link_from: NodeType,
    link_to: NodeType,
    preserve_existing: bool = False) \
        -> int:
    """
    Link from output node to input node.
    If no sockets are specified, this will match as many as it can find.
    If multiple inputs or outputs are set, matches will only be set for
    matching types.
    Adding a connection that changes the type requires connecting
    specific sockets (one out to one in).
    Will not create new links from output or to input sockets if
    `preserve_existing` is set.
    """
    connections = 0

    output_sockets = []
    input_sockets = []

    # get output sockets
    if isinstance(link_from, NodeSocket):
        if link_from.is_output:
            output_sockets.append(link_from)
    elif isinstance(link_from, Node):
        for output in link_from.outputs:
            output_sockets.append(output)
    else:
        _, _, output_sockets = resolve_node(tree, link_from)

    output_sockets = _label_sockets(output_sockets, preserve_existing)

    # get input sockets
    if isinstance(link_to, NodeSocket):
        if not link_to.is_output:
            input_sockets.append(link_to)
    elif isinstance(link_to, Node):
        for input in link_to.inputs:
            input_sockets.append(input)
    else:
        _, input_sockets, _ = resolve_node(tree, link_to)

    input_sockets = _label_sockets(input_sockets, preserve_existing)

    for output_data in output_sockets:
        output, out_matched = output_data
        if out_matched:
            continue
        for input_data in input_sockets:
            input, matched = input_data
            if matched:
                continue

            if output.type == input.type \
                or (len(output_sockets) == 1 and len(input_sockets) == 1):
                tree.links.new(output, input)
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
        _, inputs, outputs = resolve_node(tree, of)
        for input in inputs:
            links.extend(input.links)
        for output in outputs:
            links.extend(output.links)

    return links

def remove_links(tree: NodeTree, node: NodeType) -> int:
    removed = 0
    for link in get_links(tree, node):
        tree.links.remove(link)
        removed += 1

    return removed

def get_socket(tree: NodeTree, node_str: str) -> NodeSocket:
    return get_sockets(tree, node_str)[0]

def get_sockets(tree: NodeTree, node_str: str) -> List[NodeSocket]:
    _, inputs, outputs = resolve_node(tree, node_str)
    inputs.extend(outputs)
    return inputs

def get_input_sockets(tree: NodeTree, node_str: str) -> List[NodeSocket]:
    return resolve_node(tree, node_str)[1]

def get_output_sockets(tree: NodeTree, node_str: str) -> List[NodeSocket]:
    return resolve_node(tree, node_str)[2]

def get_node(tree: NodeTree, node_str: str) -> Node:
    """
    Retrieve the the Node from tree at the given `node_str`.

    raises ValueError if `node_path` is invalid.
    """
    return resolve_node(tree, node_str)[0]

def resolve_node(tree: NodeTree, node_str: str) \
    -> Tuple[Node, List[NodeSocket], List[NodeSocket]]:
    """
    In the context of `tree`, get the Node and input and/or output sockets
    of the `node_str`.

    Return:
    Tuple containing (Node, `Socket`s, output `Socket`s)
    """

    node_name, socket_name, socket_index, include_inputs, include_outputs = \
        _parse_node_str(node_str)

    if node_name not in tree.nodes:
        _invalid_node_str(node_str,
            "Node name ({}) not found".format(node_name))

    node = tree.nodes[node_name]

    inputs = []
    outputs = []

    _append_matching_sockets(socket_name, socket_index, include_inputs, node.inputs, inputs)
    _append_matching_sockets(socket_name, socket_index, include_outputs, node.outputs, outputs)

    return (node, inputs, outputs)

# helpers ↓

def _append_matching_sockets(
    socket_name: str,
    socket_index: str,
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

def _format_socket_str(node, socket, symbol):
    if isinstance(socket, str):
        return '{}{}{}{}'.format(
            symbol, node, SOCKET_DELIMETER, socket)

    return '{}{}'.format(symbol, node)

def _invalid_node_str(node_str, message):
    raise ValueError("Invalid Node Str: {}\n{}".format(node_str, message))

def _is_union_instance(item, union_type) -> bool:
    """
    Check if `item` is of any of the types contained in a Union
    definition `union_type`.
    """
    if not get_origin(union_type) is Union:
        raise TypeError("Expected Union type")

    return isinstance(item, get_args(union_type))

def _label_sockets(sockets: List[NodeSocket], preserve_existing: bool)\
    -> List[Tuple[NodeSocket,bool]]:
    out: List[Tuple[NodeSocket,bool]] = []
    for i in range(len(sockets)):
        out.append((
            sockets[i],
            preserve_existing and len(sockets[i].links) > 0))
    return out

def _parse_node_str(node_str: str) -> Tuple[str, str, int, bool, bool]:
    input = True
    output = True
    socket = None
    socket_index = -1
    node = None

    if node_str[0] == INPUT_SYMBOL:
        output = False
        node_str = node_str[1:]
    elif node_str[0] == OUTPUT_SYMBOL:
        input = False
        node_str = node_str[1:]

    parts = node_str.split(SOCKET_DELIMETER)
    if len(parts) > 1:
        socket = parts[-1]
        node = SOCKET_DELIMETER.join(parts[:-1])
    else:
        node = node_str

    if socket is not None:
        left_bracket = socket.find('[')
        right_bracket = socket.find(']')

        if left_bracket >= 0 and right_bracket >= 2:
            socket_index = int(socket[left_bracket+1:right_bracket])
            socket = socket[:left_bracket]

    return (node, socket, socket_index, input, output)