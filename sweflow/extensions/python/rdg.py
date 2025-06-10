from pathlib import Path
from typing import List, Dict, Set

import networkx as nx


def generate_uuid(item: Dict) -> str:
    """
    Generate a unique identifier for the item. The item must contain the following keys:
    - filepath: the absolute path of the file.
    - lineno: the line number.
    - func_name: the function name, if the item is a function else class method name.
    """
    uuid = f"{item['filepath']}:{item['lineno']}:{item['func_name']}"
    return uuid


class RuntimeDependencyGraph():

    def __init__(self, trace: None | Dict = None):
        """
        Initialize the runtime dependency graph.
        """
        if trace is not None:
            self.graph = self.build_graph(trace)
        else:
            self.graph = None

    def build_graph(self, trace: Dict) -> nx.DiGraph:
        """
        Build the dependency graph from the trace.
        """
        dependencies = {}
        call_relations = trace['call-relations']
        for call_relation in call_relations:
            caller_id = generate_uuid(call_relation['caller'])
            callee_id = generate_uuid(call_relation['callee'])
            if caller_id not in dependencies:
                dependencies[caller_id] = set()
            dependencies[caller_id].add(callee_id)

        dependency_graph = nx.DiGraph()
        for caller, callees in dependencies.items():
            for callee in callees:
                dependency_graph.add_edge(caller, callee)

        return dependency_graph


def get_test_nodes(rdg: RuntimeDependencyGraph) -> List[str]:
    """
    Get the test function nodes.
    """
    test_nodes = []
    for node in rdg.graph.nodes:
        filepath, lineno, func_name = node.split(':')
        path_parts = Path(filepath).parts
        filename = Path(filepath).name
        if any(part.startswith('test') or part.endswith('test') for part in path_parts):
            test_nodes.append(node)
        elif filename.startswith('test') or filename.endswith('test'):
            test_nodes.append(node)
    return test_nodes


def get_target_test_nodes(rdg: RuntimeDependencyGraph, root_nodes: List[str]) -> List[str]:
    """
    Get the target test nodes.
    """
    return root_nodes


def get_dependent_test_nodes(rdg: RuntimeDependencyGraph, root_nodes: List[str]) -> List[str]:
    """
    Get the dependent test nodes.
    """
    test_nodes = get_test_nodes(rdg)
    target_test_nodes = get_target_test_nodes(rdg, root_nodes)
    return [node for node in test_nodes if node not in target_test_nodes]


def get_core_nodes(rdg: RuntimeDependencyGraph) -> List[str]:
    """
    Get the core nodes.
    """
    test_nodes = get_test_nodes(rdg)
    return list(set(rdg.graph.nodes) - set(test_nodes))


def get_target_core_nodes(rdg: RuntimeDependencyGraph, root_nodes: List[str]) -> List[str]:
    """
    Get the target core nodes.
    """
    test_nodes = get_test_nodes(rdg)
    candidates = set()
    for root_node in root_nodes:
        candidates.update(rdg.graph.successors(root_node))
    return list(candidates - set(test_nodes))


def get_dependent_core_nodes(rdg: RuntimeDependencyGraph, root_nodes: List[str]) -> List[str]:
    """
    Get the dependent core nodes.
    """
    core_nodes = get_core_nodes(rdg)
    target_core_nodes = get_target_core_nodes(rdg, root_nodes)
    return list(set(core_nodes) - set(target_core_nodes))
