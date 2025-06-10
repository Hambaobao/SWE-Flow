import argparse
import json
from collections import defaultdict
from typing import List, Dict
from pathlib import Path
from tqdm import tqdm

SWEEFLOW_REPOS = [
    "arrow-py/arrow",
    "pyca/cryptography",
    "librosa/librosa",
    "marshmallow-code/marshmallow",
    "mwaskom/seaborn",
    "python-pillow/Pillow",
    "piskvorky/gensim",
    "pydantic/pydantic",
    "pallets/jinja",
    "pytransitions/transitions",
    "pylint-dev/pylint",
    "pandas-dev/pandas",
]


def make_sweflow_bench(data: List[Dict], output_file: str = "data/sweflow-bench.jsonl"):

    sweflow_bench_data = []
    stats = defaultdict(int)
    for item in tqdm(data):
        if item["repo"] in SWEEFLOW_REPOS:
            stats[item["repo"]] += 1
            sweflow_bench_data.append(item)

    with open(output_file, "w") as f:
        for item in sweflow_bench_data:
            f.write(json.dumps(item) + "\n")

    with open(f"{str(output_file).strip('.jsonl')}.stats.json", "w") as f:
        json.dump(stats, f, indent=4)


def make_sweflow_bench_lite(data: List[Dict], output_file: str = "data/sweflow-bench-lite.jsonl"):

    sweflow_bench_data = []
    stats = defaultdict(int)
    for item in tqdm(data):
        if item["repo"] in SWEEFLOW_REPOS:
            stats[item["repo"]] += 1
            if stats[item["repo"]] > 50:
                continue
            sweflow_bench_data.append(item)

    with open(output_file, "w") as f:
        for item in sweflow_bench_data:
            f.write(json.dumps(item) + "\n")

    with open(f"{str(output_file).strip('.jsonl')}.stats.json", "w") as f:
        json.dump(stats, f, indent=4)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-file", type=str, default="data/sweflow.jsonl")
    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    with open(args.input_file, "r") as f:
        data = [json.loads(line) for line in tqdm(f)]

    make_sweflow_bench(data, Path(args.input_file).parent / "sweflow-bench.jsonl")

    make_sweflow_bench_lite(data, Path(args.input_file).parent / "sweflow-bench-lite.jsonl")
