# ©2021-2022 Dustin Walde
# Licensed under GPL-3.0

import sys

from typing import (
    Dict,
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
SOCKET_DELIMITER = ':'

def get_node(tree: NodeTree, of: NodeType) -> Node:
    """
    Retrieve the the Node from tree at the given `node_str`.

    raises ValueError if `node_path` is invalid.
    """
    return _resolve_node(tree, of)['node']

def get_sockets(tree: NodeTree, of: str) -> List[NodeSocket]:
    node_data = _resolve_node(tree, of)
    node_data['input_sockets'].extend(node_data['output_sockets'])
    return node_data['input_sockets']

def get_socket(tree: NodeTree, of: str) -> Optional[NodeSocket]:
    sockets = get_sockets(tree, of)
    if len(sockets) == 0:
        return None
    return sockets[0]

def get_links(tree: NodeTree, of: NodeType) -> List[NodeLink]:
    node_data = _resolve_node(tree, of)
    node_data['input_links'].extend(node_data['output_links'])
    return node_data['input_links']

def get_link(tree: NodeTree, of: NodeType) -> Optional[NodeLink]:
    links = get_links(tree, of)
    if len(links) == 0:
        return None
    return links[0]

def get_subtree(tree: NodeTree, of: NodeType) -> Optional[NodeTree]:
    node = _resolve_node(tree, of)['node']
    if is_group(node):
        return node.node_tree
    else:
        return None

def is_group(node: Node) -> bool:
    """
    Check if node is a *GroupNode of some sort.
    """
    return _is_union_instance(node, NodeGroupType)

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

    from_data = _resolve_node(tree, link_from)
    output_sockets = _label_sockets(from_data['output_sockets'], preserve_existing)

    to_data = _resolve_node(tree, link_to)
    input_sockets = _label_sockets(to_data['input_sockets'], preserve_existing)

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

def remove_links(tree: NodeTree, of: NodeType, to: Optional[NodeType] = None) -> int:
    removed = 0
    if to is not None:
        to = _resolve_node(tree, to)["node"]

    for link in get_links(tree, of):
        if to is None or link.to_node == to:
            tree.links.remove(link)
            removed += 1

    return removed

# helpers ↓

def _append_matching_sockets(
    socket_name: str,
    socket_index: str,
    include: bool,
    node_sockets: Union[NodeInputs,NodeOutputs],
    out_sockets: List[NodeSocket],
    out_links: List[NodeLink]):
    name_count = 0
    if include:
        for socket in node_sockets:
            if socket_name is None or socket_name == socket.name:
                if socket_index < 0 or socket_index == name_count:
                    out_sockets.append(socket)
                    out_links.extend(socket.links)
                name_count += 1

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

    parts = node_str.split(SOCKET_DELIMITER)
    if len(parts) > 1:
        socket = parts[-1]
        node = SOCKET_DELIMITER.join(parts[:-1])
    else:
        node = node_str

    if socket is not None:
        left_bracket = socket.find('[')
        right_bracket = socket.find(']')

        if left_bracket >= 0 and right_bracket >= 2:
            socket_index = int(socket[left_bracket+1:right_bracket])
            socket = socket[:left_bracket]

    return (node, socket, socket_index, input, output)

def _resolve_node(tree: NodeTree, node: NodeType) \
    -> Dict[str, Union[Node, List[NodeSocket], List[NodeLink]]]:
    """
    In the context of ``tree``, get the Node and input and/or output sockets
    of the `node`.

    Return:
    Tuple containing (Node, ``Socket``s, output ``Socket``s)
    """

    inputs = []
    outputs = []
    input_links = []
    output_links = []

    if isinstance(node, str):
        node_name, socket_name, socket_index, include_inputs, include_outputs = \
            _parse_node_str(node)

        if node_name not in tree.nodes:
            _invalid_node_str(node,
                "Node name ({}) not found".format(node_name))

        node = tree.nodes[node_name]
        _append_matching_sockets(socket_name, socket_index, include_inputs, node.inputs, inputs, input_links)
        _append_matching_sockets(socket_name, socket_index, include_outputs, node.outputs, outputs, output_links)
    elif isinstance(node, Node):
        outputs.extend(node.outputs)
        inputs.extend(node.inputs)
        input_links.extend(filter(lambda a: a.to_node == node, node.links))
        output_links.extend(filter(lambda a: a.from_node == node, node.links))
    elif isinstance(node, NodeSocket):
        if node.is_output:
            outputs.append(node)
            output_links.extend(node.links)
        else:
            inputs.append(node)
            input_links.extend(node.links)
        node = node.node

    return {
        "node": node,
        "input_links": input_links,
        "input_sockets": inputs,
        "output_links": output_links,
        "output_sockets": outputs,
    }
