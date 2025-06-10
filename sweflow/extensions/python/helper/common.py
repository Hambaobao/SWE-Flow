from typing import Dict, List
from pathlib import Path

import difflib


def collect_nodes(development_plans: Dict[str, List[str]], key: str = 'core-nodes') -> List[str]:
    """
    Collect all the nodes from the development plans.
    Args:
        development_plans: The development plans.
        key: The key to collect the nodes from.
    Returns:
        A list of all the nodes.
    """
    all_nodes = []
    for plan in development_plans:
        all_nodes.extend(plan[key])
    all_nodes = list(set(all_nodes))
    return all_nodes


def read_file_from_project(project_root: str, filepath: str) -> str:
    """
    Read a file from the project root.
    Args:
        project_root: The root directory of the project.
        filepath: The path to the file to read.
    Returns:
        The content of the file.
    """
    with open(Path(project_root) / filepath, "r", encoding="utf-8") as f:
        return f.read()


def aggregate_nodes_by_file(nodes: List[str]) -> Dict[str, List[str]]:
    """
    Aggregate the nodes by file.
    """
    nodes_by_file = {}
    for node in nodes:
        filename, lineno, func_name = node.split(':')
        if filename not in nodes_by_file:
            nodes_by_file[filename] = []
        nodes_by_file[filename].append(node)
    return nodes_by_file


def generate_patch(skeleton_files: List[Dict[str, str]], reference_files: List[Dict[str, str]]) -> str:
    """
    Generate a unified diff patch that supports creating, modifying, and deleting files.

    Args:
        skeleton_files (List[Dict[str, str]]): List of dictionaries mapping file names to their content for skeleton files.
        reference_files (List[Dict[str, str]]): List of dictionaries mapping file names to their content for reference files.

    Returns:
        str: A unified diff patch representing the differences between the two sets of files.
    """
    # Collect all file names from both skeleton_files and groundtruth_files
    skeleton_files_dict = {skeleton_file['filepath']: skeleton_file['content'] for skeleton_file in skeleton_files}
    reference_files_dict = {reference_file['filepath']: reference_file['content'] for reference_file in reference_files}

    # Compute the union of file names
    all_filenames = set(skeleton_files_dict.keys()).union(set(reference_files_dict.keys()))

    patches = []

    for filename in sorted(all_filenames):
        # Retrieve content for the current file
        skeleton_content = skeleton_files_dict.get(filename, "")
        reference_content = reference_files_dict.get(filename, "")

        if filename not in skeleton_files_dict:
            # Handle new files
            diff = difflib.unified_diff(
                [],
                reference_content.splitlines(),
                fromfile="/dev/null",
                tofile=f"{filename}",
                lineterm="",
            )
        elif filename not in reference_files_dict:
            # Handle file deletion
            diff = difflib.unified_diff(
                skeleton_content.splitlines(),
                [],
                fromfile=f"{filename}",
                tofile="/dev/null",
                lineterm="",
            )
        else:
            # Handle file modifications
            diff = difflib.unified_diff(
                skeleton_content.splitlines(),
                reference_content.splitlines(),
                fromfile=f"{filename}",
                tofile=f"{filename}",
                lineterm="",
            )

        patch_content = "\n".join(diff)
        if patch_content:
            patches.append(patch_content)

    patch = "\n".join(patches) + "\n"  # Ensure patch ends with a newline

    return patch


def convert_patch_to_replace(patch: str) -> str:
    """
    Converts a unified-diff patch into a 'replace' formatted content.
    
    Args:
        patch (str): The patch-formatted content.
    
    Returns:
        str: The replace-formatted content.
    """
    lines = patch.splitlines()

    files_diffs = []

    current_old_file = None
    current_new_file = None
    current_file_data = None  # used to collect all chunks of the current file
    in_hunk = False  # mark if current is processing a hunk

    # temporary storage for current hunk's search/replace
    search_lines = []
    replace_lines = []

    def finish_hunk():
        """
        store the current hunk (search_lines, replace_lines) into the current file data structure.
        """
        if search_lines or replace_lines:
            current_file_data['chunks'].append((search_lines[:], replace_lines[:]))
            search_lines.clear()
            replace_lines.clear()

    def finish_file():
        """
        finish the current file's collection and store it into files_diffs.
        """
        if current_file_data:
            # if the last hunk is not finished, finish it first
            finish_hunk()
            if current_file_data['chunks']:
                files_diffs.append(current_file_data)

    idx = 0
    while idx < len(lines):
        line = lines[idx]

        if line.startswith('--- '):
            # a new file diff starts
            # if there is a file not finished, finish it first
            finish_file()

            # extract the old file name
            # for example, line is like: --- path/to/file1.py
            current_old_file = line[4:].strip()
            # prepare a new file diff container
            current_file_data = {
                'filename': None,  # not sure yet, will be set after +++
                'chunks': []
            }
            in_hunk = False

        elif line.startswith('+++ '):
            # extract the new file name
            current_new_file = line[4:].strip()
            # set the real filename, usually the old file and new file are the same, which means modification
            # if the new file is /dev/null, it may represent deletion, if the old file is /dev/null, it may represent addition
            # for simplicity, here directly use new_file as filename when it is not /dev/null, otherwise use old_file
            if current_new_file != '/dev/null':
                current_file_data['filename'] = current_new_file
            else:
                current_file_data['filename'] = current_old_file

            in_hunk = False

        elif line.startswith('@@ '):
            # a new hunk, finish the last hunk first and then start the next one
            finish_hunk()
            in_hunk = True
            # @@ -1,4 +1,4 @@ this line can parse line numbers, but here we do not go deep into it, just skip it
            # different blocks will be stored in (search, replace) separately
            # no extra work is needed, just move to the next one
        else:
            # if in hunk area, process the line, otherwise it may be an empty line or other, here simply skip it
            if in_hunk and current_file_data is not None:
                if line.startswith('-'):
                    # minus line -> only put into search
                    search_lines.append(line[1:])
                elif line.startswith('+'):
                    # plus line -> only put into replace
                    replace_lines.append(line[1:])
                else:
                    # no +/- prefix (or space prefix) -> put into both search & replace
                    # according to the standard of unified diff, context line usually starts with ' '
                    # here simply remove the possible leading space
                    search_lines.append(line[1:])
                    replace_lines.append(line[1:])

        idx += 1

    # there may still be the last file/last hunk not written
    finish_file()

    # start to convert files_diffs to the final output format
    output_lines = []
    for file_diff in files_diffs:
        filename = file_diff['filename']
        chunks = file_diff['chunks']
        output_lines.append(f'```replace: {filename}')
        for (s_lines, r_lines) in chunks:
            output_lines.append('<<<<<<< SEARCH')
            output_lines.extend(s_lines)
            output_lines.append('=======')
            output_lines.append('>>>>>>> REPLACE')
            output_lines.extend(r_lines)
        output_lines.append('```')  # end the replace block of this file

    return '\n'.join(output_lines)


def generate_test_script(test_ids: List[str]) -> str:
    """
    Generate a test script to verify the skeletonization.

    :param test_ids: List of test ids.
    """
    test_checkpoints = [test_id for test_id in test_ids]

    test_script = " ".join(["python", "-m", "pytest"] + test_checkpoints)

    return test_script
