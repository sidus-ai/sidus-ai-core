import networkx as nx

__separator__ = '__$'
__in__ = 'in'
__out__ = 'out'


class AgentSkillGraph:
    """
    Skill graph formation container
    """

    def __init__(
        self,
        full_skill_names: list,
        available_skill_names: list = None,
        weight_for_not_use_nodes: int = 100,
        weight_for_used_nodes: int = 1
    ):
        self.depth = max_skill_contains(available_skill_names)

        nodes = build_repeatable_nodes_names(full_skill_names, self.depth)
        edges = build_edges(nodes, weight=weight_for_not_use_nodes)

        update_edges_at_skill(available_skill_names, edges, weight=weight_for_used_nodes)

        self.graph = nx.Graph()
        self.graph.add_weighted_edges_from(edges)

        # TODO: Print graph to console
        #   use nx.write_network_text(self.graph)

    def get_active_nodes(self):
        """
        :return: Get a list of available skills from the graph
        """
        _path = list(nx.dijkstra_path(self.graph, __in__, __out__))
        return [
            v.split(
                __separator__
            )[0] if __separator__ in v else v for v in _path if v not in [__in__, __out__]
        ]

    def get_skill_weight(self, from_skill_name: str, to_skill_name: str):
        return self.graph[from_skill_name][to_skill_name]['weight']

    def set_skill_weight(self, from_skill_name: str, to_skill_name: str, weight):
        self.graph[from_skill_name][to_skill_name]['weight'] = weight


def max_skill_contains(skills: list) -> int:
    """
    Gets the maximum number of skill inclusions.
    Used to include repetitions in the list of available skills.
    :param skills:
    :return:
    """
    _s = [skills.count(s) for s in skills]
    return max(_s)


def build_edges(nodes: list, weight: int = 100):
    edges = []
    build_node_with_weight(__in__, nodes, edges, weight)
    for i, _node in enumerate(nodes):
        build_node_with_weight(_node, nodes, edges, weight)
    build_node_with_weight(__out__, nodes, edges, weight)
    return edges


def build_repeatable_nodes_names(nodes: list, depth: int):
    """
    We set the number of vertices, taking into account the repetition of the use of skills
    :param nodes:
    :param depth:
    :return:
    """
    _nodes = []
    for node in nodes:
        for i in range(depth):
            _nodes.append(f'{node}{__separator__}{i}')
    return _nodes


def build_node_with_weight(from_node, to_nodes, edges, weight: int = 100):
    """
    Generate weighted edges from a vertex to a specified list of vertices
    :param from_node:
    :param to_nodes:
    :param edges: Current list of weighted edges
    :param weight:
    :return:
    """
    for _node_next in to_nodes:
        if from_node == _node_next:
            continue
        _edge = (from_node, _node_next, weight)
        edges.append(_edge)


def build_skill_names_at_index(skills: list):
    """
    Forming a list of vertices with a repeat inclusion index
    :param skills:
    :return:
    """
    _available_nodes = []
    _contains_available_nodes = {s: 0 for s in set(skills)}
    for skill in skills:
        _available_nodes.append(f'{skill}{__separator__}{_contains_available_nodes[skill]}')
        _contains_available_nodes[skill] += 1
    _available_nodes.append(__out__)
    return _available_nodes


def update_edges_at_skill(skills: list, edges, weight: int = 1):
    """
    Updating edge weights for skill list
    :param skills:
    :param edges:
    :param weight:
    :return:
    """
    prev = __in__
    _available_nodes = build_skill_names_at_index(skills)
    for skill in _available_nodes:
        for index, edge in enumerate(edges):
            _in, _out, _weight = edge
            if (_in == prev and _out == skill) or (_in == skill and _out == prev):
                edges[index] = (_in, _out, weight)
        prev = skill
