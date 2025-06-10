from pathlib import Path
from tempfile import TemporaryDirectory

import argparse
import shutil
import json
from copy import deepcopy

from sweflow.utils.progress import create_progress
from sweflow.utils.token_utils import TokenCounter
from sweflow.extensions.python.helper import (
    clean_codebase,
    reinit_codebase,
    update_codebase_on_schedule,
    skeletonize_codebase_on_schedule,
    generate_patch,
)


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument("--project-root", type=str, required=True, help="Path to the repository")
    parser.add_argument("--development-schedule", type=str, required=True, help="Path to the development schedule")
    parser.add_argument("--docstrings", type=str, required=True, help="Path to the docstrings")
    parser.add_argument("--output-codebase-dir", type=str, required=True, help="Path to the output codebase directory")
    parser.add_argument("--temp-dir", type=str, default=None, help="Path to the temporary directory")
    parser.add_argument("--output-dir", type=str, default=None, help="Path to the output directory")

    return parser.parse_args()


def main():

    args = parse_args()

    with open(args.development_schedule, "r") as f:
        development_schedule = json.load(f)

    with open(args.docstrings, "r") as f:
        docstrings = json.load(f)

    (
        skeleton_files,
        reference_files,
        reference_patches,
        fail_to_pass_test_ids,
        pass_to_pass_test_ids,
        base_commits,
        reference_commits,
        step_flags,
    ) = ([], [], [], [], [], [], [], [])

    _pass_to_pass_test_ids = []
    # create a temporary directory for operations
    Path(args.temp_dir).mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=args.temp_dir) as codebase_dir:
        clean_codebase(args.project_root)
        repo = reinit_codebase(args.project_root, codebase_dir)
        with create_progress() as progress:
            task = progress.add_task("[cyan]Preparing codebase...", total=len(development_schedule))
            for schedule in development_schedule:
                # skeletonize the codebase
                schedule_skeleton_files, schedule_reference_files = skeletonize_codebase_on_schedule(args.project_root, schedule, docstrings)
                skeleton_files.append({"step": schedule['step'], "skeleton-files": schedule_skeleton_files})
                reference_files.append({"step": schedule['step'], "reference-files": schedule_reference_files})
                # update the codebase
                commit_info = update_codebase_on_schedule(repo, schedule, schedule_skeleton_files, schedule_reference_files)
                # commit_info.update({"step": schedule['step']})
                base_commits.append({"step": schedule['step'], "base-commit": commit_info['base-commit']})
                reference_commits.append({"step": schedule['step'], "reference-commit": commit_info['reference-commit']})
                # generate the reference patch
                reference_patch = generate_patch(schedule_skeleton_files, schedule_reference_files)
                reference_patches.append({"step": schedule['step'], "reference-patch": reference_patch})
                # generate the fail-to-pass test ids
                fail_to_pass_test_ids.append({"step": schedule['step'], "fail-to-pass-test-ids": schedule['test-ids']})
                # generate the pass-to-pass test ids (accumulate)
                pass_to_pass_test_ids.append({"step": schedule['step'], "pass-to-pass-test-ids": deepcopy(_pass_to_pass_test_ids)})
                _pass_to_pass_test_ids.extend(schedule['test-ids'])
                # flag the step
                flag = False if TokenCounter.count_tokens(reference_patch) < 10 else True
                step_flags.append({"step": schedule['step'], "flag": flag})
                # update the progress
                progress.update(task, advance=1)

        Path(args.output_codebase_dir).mkdir(parents=True, exist_ok=True)
        # zip the codebase
        output_codebase = Path(args.output_codebase_dir) / "codebase.zip"
        shutil.make_archive(output_codebase.with_suffix(""), "zip", codebase_dir)

        # zip the original codebase
        output_original_codebase = Path(args.output_codebase_dir) / "codebase.origin.zip"
        shutil.make_archive(output_original_codebase.with_suffix(""), "zip", args.project_root)

    # save skeleton files
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(args.output_dir) / "skeleton-files.json", "w") as f:
        json.dump(skeleton_files, f)

    # save reference files
    with open(Path(args.output_dir) / "reference-files.json", "w") as f:
        json.dump(reference_files, f)

    # save reference patches
    with open(Path(args.output_dir) / "reference-patches.json", "w") as f:
        json.dump(reference_patches, f)

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

    # save step flags
    with open(Path(args.output_dir) / "step-flags.json", "w") as f:
        json.dump(step_flags, f)


if __name__ == "__main__":

    main()
