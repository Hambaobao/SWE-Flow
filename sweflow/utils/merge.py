from typing import Dict, List
from pathlib import Path

import json
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Merge JSON dataset to JSONL file")
    parser.add_argument("--repository", type=str, help="The full name of the repository")
    parser.add_argument("--input-dir", type=str, help="Path to the input directory")
    parser.add_argument("--output-file", type=str, help="Path to the output JSONL file")
    return parser.parse_args()


def merge_to_jsonl(repository: str, input_dir: str, output_file: str):
    """
    Load a JSON data files.
    """
    # step flags
    with open(Path(input_dir) / "step-flags.json", "r") as f:
        step_flags = [item['flag'] for item in json.load(f)]
    # specifications
    with open(Path(input_dir) / "specifications.json", "r") as f:
        specifications = [item['specification'] for item in json.load(f) if step_flags[item['step']]]
    # base commits
    with open(Path(input_dir) / "base-commits.json", "r") as f:
        base_commits = [item['base-commit'] for item in json.load(f) if step_flags[item['step']]]
    # reference commits
    with open(Path(input_dir) / "reference-commits.json", "r") as f:
        reference_commits = [item['reference-commit'] for item in json.load(f) if step_flags[item['step']]]
    # fail-to-pass test ids
    with open(Path(input_dir) / "fail-to-pass-test-ids.json", "r") as f:
        fail_to_pass_test_ids = [item['fail-to-pass-test-ids'] for item in json.load(f) if step_flags[item['step']]]
    # pass-to-pass test ids
    with open(Path(input_dir) / "pass-to-pass-test-ids.json", "r") as f:
        pass_to_pass_test_ids = [item['pass-to-pass-test-ids'] for item in json.load(f) if step_flags[item['step']]]
    # reference patches
    with open(Path(input_dir) / "reference-patches.json", "r") as f:
        reference_patches = [item['reference-patch'] for item in json.load(f) if step_flags[item['step']]]

    # all data must have the same length
    assert len(specifications) \
        == len(base_commits) == len(reference_commits) \
        == len(fail_to_pass_test_ids) == len(pass_to_pass_test_ids) \
        == len(reference_patches)

    data = []
    for step, (
            specification,
            base_commit,
            reference_commit,
            fail_to_pass_test_ids,
            pass_to_pass_test_ids,
            reference_patch,
    ) in enumerate(
            zip(
                specifications,
                base_commits,
                reference_commits,
                fail_to_pass_test_ids,
                pass_to_pass_test_ids,
                reference_patches,
            ),
            start=1,
    ):
        data.append({
            "instance_id": f"{repository.replace('/', '__--__')}-dev-{step}",
            "repo": repository,
            "problem_statement": specification,
            "base_commit": base_commit,
            "reference_commit": reference_commit,
            "patch": reference_patch,
            "fail_to_pass": fail_to_pass_test_ids,
            "pass_to_pass": pass_to_pass_test_ids,
        })

    with open(output_file, "w") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")


def main():

    args = parse_args()
    print(f"Processing dataset: {args.repository}")

    merge_to_jsonl(args.repository, args.input_dir, args.output_file)


if __name__ == "__main__":

    main()
