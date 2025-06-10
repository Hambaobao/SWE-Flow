from pathlib import Path
from tempfile import TemporaryDirectory

import argparse
import json
import subprocess
from copy import deepcopy

from sweflow.utils.progress import create_progress
from sweflow.utils.token_utils import TokenCounter


def get_commit_hash(branch: str, cwd: str = "/workspace") -> str:
    # get the commit hash of the branch
    subprocess.run(["git", "checkout", branch], cwd=cwd, check=True)
    commit_hash = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True).stdout.strip()
    return commit_hash


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--project-root", type=str, required=True, help="Path to the repository")
    parser.add_argument("--development-schedule", type=str, required=True, help="Path to the development schedule")
    parser.add_argument("--reference-patches", type=str, required=True, help="Path to the reference patches")
    parser.add_argument("--temp-dir", type=str, default=None, help="Path to the temporary directory")
    parser.add_argument("--output-dir", type=str, default=None, help="Path to the output directory")

    return parser.parse_args()


def main():

    args = parse_args()

    with open(args.development_schedule, "r") as f:
        development_schedule = json.load(f)

    with open(args.reference_patches, "r") as f:
        reference_patches = json.load(f)

    (
        fail_to_pass_test_ids,
        pass_to_pass_test_ids,
        base_commits,
        reference_commits,
        step_flags,
    ) = ([], [], [], [], [])

    _pass_to_pass_test_ids = []
    # create a temporary directory for operations
    Path(args.temp_dir).mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=args.temp_dir) as codebase_dir:
        with create_progress() as progress:
            task = progress.add_task("[cyan]Preparing codebase...", total=len(development_schedule))
            assert len(development_schedule) == len(reference_patches), f"Development schedule and reference patches must have the same length"
            for schedule, reference_patch in zip(development_schedule, reference_patches):
                assert schedule['step'] == reference_patch['step'], f"Step {schedule['step']} is not equal to patch step {reference_patch['step']}"
                # get the commit hash of the base and reference branches
                base_commits.append({"step": schedule['step'], "base-commit": get_commit_hash(f"step-{schedule['step']}-skeleton")})
                reference_commits.append({"step": schedule['step'], "reference-commit": get_commit_hash(f"step-{schedule['step']}-reference")})
                # get the fail-to-pass test ids
                fail_to_pass_test_ids.append({"step": schedule['step'], "fail-to-pass-test-ids": schedule['test-ids']})
                # get the pass-to-pass test ids (accumulate)
                pass_to_pass_test_ids.append({"step": schedule['step'], "pass-to-pass-test-ids": deepcopy(_pass_to_pass_test_ids)})
                _pass_to_pass_test_ids.extend(schedule['test-ids'])
                # get the flag of the step
                flag = False if TokenCounter.count_tokens(reference_patch['reference-patch']) < 10 else True
                step_flags.append({"step": schedule['step'], "flag": flag})
                # update the progress
                progress.update(task, advance=1)

    # save fail-to-pass test ids
    with open(Path(args.output_dir) / "fail-to-pass-test-ids.json", "w") as f:
        json.dump(fail_to_pass_test_ids, f)

    # save pass-to-pass test ids
    with open(Path(args.output_dir) / "pass-to-pass-test-ids.json", "w") as f:
        json.dump(pass_to_pass_test_ids, f)

    # save base commits
    with open(Path(args.output_dir) / "base-commits.json", "w") as f:
        json.dump(base_commits, f)

    # save reference commits
    with open(Path(args.output_dir) / "reference-commits.json", "w") as f:
        json.dump(reference_commits, f)


if __name__ == "__main__":

    main()
