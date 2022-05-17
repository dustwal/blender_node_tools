NNAAMMEE
    blender_node_tools

DDEESSCCRRIIPPTTIIOONN
    # ©2021-2022 Dustin Walde
    # Licensed under GPL-3.0

FFUUNNCCTTIIOONNSS
    ffoorrmmaatt__nnooddee(node: str, input: Union[bool, str] = False, output: Union[bool, str] = False) -> str

    ggeett__iinnppuutt__ssoocckkeettss(tree: bpy_types.NodeTree, node_str: str) -> List[bpy_types.NodeSocket]

    ggeett__lliinnkk(tree: bpy_types.NodeTree, of: Union[str, bpy_types.Node, bpy_types.NodeSocket]) -> Optional[bpy.types.NodeLink]

    ggeett__lliinnkkss(tree: bpy_types.NodeTree, of: Union[str, bpy_types.Node, bpy_types.NodeSocket]) -> List[bpy.types.NodeLink]

    ggeett__nnooddee(tree: bpy_types.NodeTree, node_str: str) -> bpy_types.Node
        Retrieve the the Node from tree at the given `node_str`.

        raises ValueError if `node_path` is invalid.

    ggeett__oouuttppuutt__ssoocckkeettss(tree: bpy_types.NodeTree, node_str: str) -> List[bpy_types.NodeSocket]

    ggeett__ssoocckkeett(tree: bpy_types.NodeTree, node_str: str) -> bpy_types.NodeSocket

    ggeett__ssoocckkeettss(tree: bpy_types.NodeTree, node_str: str) -> List[bpy_types.NodeSocket]

    iiss__ggrroouupp(node: bpy_types.Node) -> bool
        Check if node is a *GroupNode of some sort.

    lliinnkk__nnooddeess(tree: bpy_types.NodeTree, link_from: Union[str, bpy_types.Node, bpy_types.NodeSocket], link_to: Union[str, bpy_types.Node, bpy_types.NodeSocket], preserve_existing: bool = False) -> int
        Link from output node to input node.
        If no sockets are specified, this will match as many as it can find.
        If multiple inputs or outputs are set, matches will only be set for
        matching types.
        Adding a connection that changes the type requires connecting
        specific sockets (one out to one in).
        Will not create new links from output or to input sockets if
        `preserve_existing` is set.

    rreemmoovvee__lliinnkkss(tree: bpy_types.NodeTree, node: Union[str, bpy_types.Node, bpy_types.NodeSocket]) -> int

    rreessoollvvee__nnooddee(tree: bpy_types.NodeTree, node_str: str) -> Tuple[bpy_types.Node, List[bpy_types.NodeSocket], List[bpy_types.NodeSocket]]
        In the context of `tree`, get the Node and input and/or output sockets
        of the `node_str`.

        Return:
        Tuple containing (Node, `Socket`s, output `Socket`s)
