from typing import List, Dict, Tuple
from collections import defaultdict
from pathlib import Path

import argparse
import networkx as nx
import json

from sweflow.extensions.python.rdg import (
    RuntimeDependencyGraph,
    get_test_nodes,
    get_target_test_nodes,
    get_dependent_test_nodes,
    get_core_nodes,
    get_target_core_nodes,
    get_dependent_core_nodes,
)
from sweflow.utils.progress import create_progress


def parse_args():
    parser = argparse.ArgumentParser(description='Generate development plan for a Python project')
    parser.add_argument('-t', '--trace-file', type=str, help='Path to the pytest trace file')
    parser.add_argument('-o', '--output-dir', type=str, help='Output directory to save the development plans')
    return parser.parse_args()


def collect_rdg_info(trace_file: str) -> List[Dict]:
    """
    Collect the information of the runtime dependency graphs.

    Args:
        trace_file: Path to the pytest trace file (json format)

    Returns:
        List of dictionaries containing the information of the runtime dependency graphs
    """
    traces = json.load(open(trace_file))

    rdg_info = []
    with create_progress() as progress:
        task = progress.add_task(f"[cyan]Collecting runtime dependency graphs...", total=len(traces))
        for trace in traces:
            progress.update(task, advance=1)
            rdg = RuntimeDependencyGraph(trace)
            if trace['test-func-id'] not in rdg.graph:
                continue

            rdg_info.append({
                'test-id': trace['test-id'],
                'root-node': trace['test-func-id'],
                'runtime-dependency-graph': rdg,
            })

    return rdg_info


def merge_runtime_dependency_graphs(rdgs: List[RuntimeDependencyGraph]) -> RuntimeDependencyGraph:
    """
    Merge multiple runtime dependency graphs.
    """
    merged_rdg = RuntimeDependencyGraph()
    merged_rdg.graph = nx.compose_all([rdg.graph for rdg in rdgs])
    return merged_rdg


def prepare_schedule_info(rdg_info: List[Dict]) -> List[Dict]:
    """
    Prepare the schedule info from the rdg info.
    """
    core_nodes_to_rdg_info = defaultdict(list)
    for info in rdg_info:
        core_nodes_to_rdg_info[frozenset(get_core_nodes(info['runtime-dependency-graph']))].append(info)

    schedule_info = []
    for core_nodes, infos in core_nodes_to_rdg_info.items():
        # initialize the merged info
        merged_info = {
            "test-ids": [],
            "root-nodes": [],
            "test-nodes": [],
            "core-nodes": [],
            "target-test-nodes": [],
            "dependent-test-nodes": [],
            "target-core-nodes": [],
            "dependent-core-nodes": [],
            "runtime-dependency-graph": None,
        }

        # merge the test ids
        for info in infos:
            merged_info['test-ids'].append(info['test-id'])
            merged_info['root-nodes'].append(info['root-node'])

        # merge the runtime dependency graphs
        dependency_graphs = [info['runtime-dependency-graph'] for info in infos]
        merged_info['runtime-dependency-graph'] = merge_runtime_dependency_graphs(dependency_graphs)

        # get the nodes
        merged_info['core-nodes'] = get_core_nodes(merged_info['runtime-dependency-graph'])
        merged_info['test-nodes'] = get_test_nodes(merged_info['runtime-dependency-graph'])
        merged_info['target-test-nodes'] = get_target_test_nodes(
            merged_info['runtime-dependency-graph'],
            merged_info['root-nodes'],
        )
        merged_info['dependent-test-nodes'] = get_dependent_test_nodes(
            merged_info['runtime-dependency-graph'],
            merged_info['root-nodes'],
        )
        merged_info['target-core-nodes'] = get_target_core_nodes(
            merged_info['runtime-dependency-graph'],
            merged_info['root-nodes'],
        )
        merged_info['dependent-core-nodes'] = get_dependent_core_nodes(
            merged_info['runtime-dependency-graph'],
            merged_info['root-nodes'],
        )

        schedule_info.append(merged_info)

    return schedule_info


def generate_development_schedule(schedule_info: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Generate the development schedule from the schedule info.
    """
    schedules, dependency_graphs = [], []
    for info in schedule_info:
        schedules.append({
            'test-ids': info['test-ids'],
            'root-nodes': info['root-nodes'],
            'test-nodes': info['test-nodes'],
            'core-nodes': info['core-nodes'],
            'target-test-nodes': info['target-test-nodes'],
            'dependent-test-nodes': info['dependent-test-nodes'],
            'target-core-nodes': info['target-core-nodes'],
            'dependent-core-nodes': info['dependent-core-nodes'],
        })

        dependency_graphs.append(info['runtime-dependency-graph'].graph)

    development_schedule = []
    development_dependency_graphs = []
    developed_core_nodes = set()
    step = 0
    for schedule, dependency_graph in zip(schedules, dependency_graphs):
        nodes_to_develop = set(schedule['core-nodes']) - developed_core_nodes
        if nodes_to_develop:
            development_schedule.append({
                'step': step,
                **schedule,
                'nodes-to-develop': list(nodes_to_develop),
            })
            development_dependency_graphs.append({
                'step': step,
                'dependency-graph': nx.readwrite.node_link_data(dependency_graph, edges="edges"),
            })
            step += 1
        developed_core_nodes.update(nodes_to_develop)

    return development_schedule, development_dependency_graphs


def main():

    args = parse_args()

    # collect the rdg info
    rdg_info = collect_rdg_info(args.trace_file)

    # prepare the schedule info
    schedule_info = prepare_schedule_info(rdg_info)

    # sort the schedule info by the number of core nodes (ascending)
    schedule_info.sort(key=lambda x: len(x["core-nodes"]))

    # generate the development schedule
    development_schedule, dependency_graphs = generate_development_schedule(schedule_info)

    print(f"Created {len(development_schedule)} development schedule.")
    with open(Path(args.output_dir) / 'development-schedule.json', 'w') as f:
        json.dump(development_schedule, f, indent=4)

    with open(Path(args.output_dir) / 'dependency-graphs.json', 'w') as f:
        json.dump(dependency_graphs, f, indent=4)

    print(f"Development schedule and dependency graphs are saved to {args.output_dir}.")


if __name__ == '__main__':

    main()
