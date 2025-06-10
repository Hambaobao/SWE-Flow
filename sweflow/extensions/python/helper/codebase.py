from typing import List, Dict
from pathlib import Path
from git import Repo

import re
import shutil

from .common import read_file_from_project
from .code_utils import skeletonize_file


def delete_core_dumps(directory_path: Path):
    """
    Delete all core dump files in the given directory.
    """
    pattern = re.compile(r'^core\.\d+$')

    for path in directory_path.rglob("core.*"):
        if path.is_file() and pattern.match(path.name):
            try:
                path.unlink()
                print(f"Deleted core dump file: {path}")
            except Exception as e:
                print(f"Failed to delete {path}: {e}")


def clean_codebase(codebase_dir: str):
    """
    Recursively delete Python cache folders and pytest cache in the given directory.
    """
    codebase = Path(codebase_dir)

    # traverse the directory and delete cache folders
    for path in codebase.rglob("*"):
        if path.name in ("__pycache__", ".pytest_cache") and path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            print(f"Deleted cache folder: {path}")

    # delete core dumps
    delete_core_dumps(codebase)


def reinit_codebase(project_root: str, codebase_dir: str = None, initial_branch: str = "main") -> Repo:
    """
    Prepare a codebase by cloning it and removing the .git directory.
    
    Args:
        project_root: The path to the project root
        codebase_dir: The path to the codebase directory to clone the repository to
    """
    # copy the codebase to temp directory
    shutil.copytree(project_root, codebase_dir, dirs_exist_ok=True)

    # initialize new git repository
    if not (Path(codebase_dir) / ".git").exists():
        repo = Repo.init(codebase_dir, initial_branch=initial_branch)
    else:
        repo = Repo(codebase_dir)
        # rename current branch to main
        repo.git.branch("-m", "main")

    # config user and email
    with repo.config_writer() as config:
        config.set_value("user", "name", "sweflow")
        config.set_value("user", "email", "sweflow@sweflow.ai")

    # create initial commit on main branch
    repo.git.add(all=True)
    repo.git.commit("-m", "Initial test commit", "--allow-empty")

    return repo


def update_codebase_with_files(repo: Repo, files_to_update: List[Dict[str, str]]):
    """
    Update files in the repository.
    
    Args:
        repo: The git repository to update files in
        files_to_update: List of dictionaries containing file paths and contents
              Each dict should have 'filepath' and 'content' keys
    """
    # update files in the repository
    for file_dict in files_to_update:
        file_path = Path(repo.working_dir) / file_dict['filepath']
        # create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # write file content
        with open(file_path, 'w') as f:
            f.write(file_dict['content'])


def update_codebase_on_schedule(repo: Repo, schedule: Dict, skeleton_files: List[Dict[str, str]], reference_files: List[Dict[str, str]]) -> Dict[str, str]:
    """
    Update a repository for a sample by checking out a new branch, writing files, and committing the changes.
    
    Args:
        repo: The git repository to prepare
        skeleton_data: The skeleton data to update the repository with
    """

    # get the main branch
    current_branch = repo.active_branch.name

    step = schedule["step"]
    # checkout to a new branch
    branch_name = f"step-{step}-skeleton"
    repo.create_head(branch_name)
    repo.heads[branch_name].checkout()
    update_codebase_with_files(repo, skeleton_files)
    # commit the changes
    repo.git.add(all=True)
    repo.git.commit("-m", f"prepare skeleton for step {step}", "--allow-empty")
    # checkout back to the current branch
    repo.heads[current_branch].checkout()
    # get commit hash
    base_commit = repo.head.commit.hexsha

    # update reference files
    branch_name = f"step-{step}-reference"
    repo.create_head(branch_name)
    repo.heads[branch_name].checkout()
    update_codebase_with_files(repo, reference_files)
    repo.git.add(all=True)
    repo.git.commit("-m", f"prepare reference for step {step}", "--allow-empty")
    # get commit hash
    reference_commit = repo.head.commit.hexsha

    # checkout back to the main branch
    repo.heads[current_branch].checkout()

    return {
        "base-commit": base_commit,
        "reference-commit": reference_commit,
    }


def skeletonize_codebase_on_schedule(
    project_root: str,
    schedule: Dict[str, str],
    docstrings: Dict[str, str],
) -> List[Dict[str, str]]:
    """
    Skeletonize a codebase, given a list of core nodes.
    """

    target_core_nodes_to_develop = list(set(schedule['target-core-nodes']) & set(schedule['nodes-to-develop']))
    dependent_core_nodes_to_develop = list(set(schedule['dependent-core-nodes']) & set(schedule['nodes-to-develop']))
    core_nodes_to_develop = target_core_nodes_to_develop + dependent_core_nodes_to_develop

    candidate_files = set()
    for node in core_nodes_to_develop:
        filepath, lineno, function_name = node.split(':')
        candidate_files.add(filepath)

    files_to_skeletonize = []
    for filepath in candidate_files:
        content = read_file_from_project(project_root, filepath)
        files_to_skeletonize.append({
            "filepath": filepath,
            "content": content,
        })

    skeleton_files, reference_files = [], []
    # process files
    for file_info in files_to_skeletonize:
        skeletonized_code, reference_code = skeletonize_file(
            file_info,
            target_core_nodes=target_core_nodes_to_develop,
            dependent_core_nodes=dependent_core_nodes_to_develop,
            docstrings=docstrings,
        )
        skeleton_files.append({"filepath": file_info["filepath"], "content": skeletonized_code})
        reference_files.append({"filepath": file_info["filepath"], "content": reference_code})

    return skeleton_files, reference_files
