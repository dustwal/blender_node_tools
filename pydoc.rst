FUNCTIONS
---------

.. code-block:: python
    def format_node(node: str, input: Union[bool, str] = False, output: Union[bool, str] = False) -> str

.. code-block:: python
    def get_input_sockets(tree: bpy_types.NodeTree, node_str: str) -> List[bpy_types.NodeSocket]

.. code-block:: python
    def get_link(tree: bpy_types.NodeTree, of: Union[str, bpy_types.Node, bpy_types.NodeSocket]) -> Optional[bpy.types.NodeLink]

.. code-block:: python
    def get_links(tree: bpy_types.NodeTree, of: Union[str, bpy_types.Node, bpy_types.NodeSocket]) -> List[bpy.types.NodeLink]

.. code-block:: python
    def get_node(tree: bpy_types.NodeTree, node_str: str) -> bpy_types.Node

Retrieve the the Node from tree at the given `node_str`.

raises ValueError if `node_path` is invalid.

.. code-block:: python
    def get_output_sockets(tree: bpy_types.NodeTree, node_str: str) -> List[bpy_types.NodeSocket]

.. code-block:: python
    def get_socket(tree: bpy_types.NodeTree, node_str: str) -> bpy_types.NodeSocket

.. code-block:: python
    def get_sockets(tree: bpy_types.NodeTree, node_str: str) -> List[bpy_types.NodeSocket]

.. code-block:: python
    def is_group(node: bpy_types.Node) -> bool

Check if node is a \*GroupNode of some sort.

.. code-block:: python
    def link_nodes(tree: bpy_types.NodeTree, link_from: Union[str, bpy_types.Node, bpy_types.NodeSocket], link_to: Union[str, bpy_types.Node, bpy_types.NodeSocket], preserve_existing: bool = False) -> int

Link from output node to input node.
If no sockets are specified, this will match as many as it can find.
If multiple inputs or outputs are set, matches will only be set for
matching types.
Adding a connection that changes the type requires connecting
specific sockets (one out to one in).
Will not create new links from output or to input sockets if
`preserve_existing` is set.

.. code-block:: python
    def remove_links(tree: bpy_types.NodeTree, node: Union[str, bpy_types.Node, bpy_types.NodeSocket]) -> int

.. code-block:: python
    def resolve_node(tree: bpy_types.NodeTree, node_str: str) -> Tuple[bpy_types.Node, List[bpy_types.NodeSocket], List[bpy_types.NodeSocket]]

In the context of `tree`, get the Node and input and/or output sockets
of the `node_str`.

Return:
Tuple containing (Node, `Socket`s, output `Socket`s)

DATA
----

.. code-block:: python
    INPUT_SYMBOL = '+'
    OUTPUT_SYMBOL = '-'
    SOCKET_DELIMETER = ':'
    NodeGroupType = typing.Union[bpy.types.CompositorNodeGroup, bpy....had...
    NodeType = typing.Union[str, bpy_types.Node, bpy_types.NodeSocket]
    List = typing.List
    Optional = typing.Optional
    Tuple = typing.Tuple
    Union = typing.Union