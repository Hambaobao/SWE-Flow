from typing import List, Dict, Any
from pathlib import Path
from fluxllm import FluxOpenAIChat

import argparse
import json

from sweflow.extensions.python.helper import (
    collect_nodes,
    read_file_from_project,
    CodeParser,
)

DATA_DIR = Path(__file__).parent / "data" / "docstring"

DEMONSTRATIONS_FILE = DATA_DIR / "demonstations.json"
with open(DEMONSTRATIONS_FILE, "r") as f:
    DEMONSTRATIONS = json.load(f)

SYSTEM_PROMPT_FILE = DATA_DIR / "system-prompt.md"
with open(SYSTEM_PROMPT_FILE, "r") as f:
    SYSTEM_PROMPT = f.read()


def request_collate(
    sample: Dict[str, Any],
    n_shots: int = 2,
    model: str = "Qwen2.5-Coder-32B-Instruct",
) -> Dict[str, Any]:
    """
    Collate the messages for the OpenAI API.
    """
    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    for demonstration in DEMONSTRATIONS[:n_shots]:
        messages.append({'role': 'user', 'content': demonstration['user']['content']})
        messages.append({'role': 'assistant', 'content': demonstration['assistant']['content']})

    messages.append({"role": "user", "content": sample['function-content']})

    return {
        "model": model,
        "messages": messages,
    }


def parse_args():

    parser = argparse.ArgumentParser(description="Generate docstrings.")

    parser.add_argument("--project-root", type=str, help="Path to the root directory of the project.")
    parser.add_argument("--development-schedule", type=str, help="Path to the JSON development schedule file.")
    parser.add_argument("--base-url", type=str, help="Base URL for the OpenAI API.")
    parser.add_argument("--api-key", type=str, help="API key for the OpenAI API.")
    parser.add_argument("--model", type=str, help="OpenAI model to use for docstring generation.")
    parser.add_argument("--max-qpm", type=int, default=256, help="Max QPM for the OpenAI API.")
    parser.add_argument("--max-retries", type=int, default=3, help="Max retries for the OpenAI API.")
    parser.add_argument("--cache-file", type=str, help="Path to the cache file.")
    parser.add_argument("--output-file", type=str, help="Path to the output file.")

    return parser.parse_args()


def load_development_schedule(development_schedule_file: str) -> Dict[str, List[str]]:
    """
    Load the development schedule from a JSON file.
    """
    print(f"Loading development schedule from `{development_schedule_file}`.")
    with open(development_schedule_file, "r") as f:
        return json.load(f)


def prepare_samples(project_root: str, development_schedule: Dict[str, List[str]]) -> List[Dict[str, str]]:
    """
    Prepare the samples for the OpenAI API.
    """
    nodes_to_develop = collect_nodes(development_schedule, key='nodes-to-develop')

    samples = []
    for node in nodes_to_develop:
        filepath, lineno, func_name = node.split(':')
        node_id = f"{filepath}:{lineno}:{func_name}"
        content = read_file_from_project(project_root=project_root, filepath=filepath)
        function_content = CodeParser.get_function_content(content, func_name, lineno)
        if function_content is None:
            print(f"Could not find function content for `{node_id}`, skipping.")
            continue
        samples.append({'node-id': node_id, 'function-content': function_content})

    return samples


def main():

    args = parse_args()

    print(f"Preparing docstrings for `{args.project_root}`.")

    # load the development plans
    development_schedule = load_development_schedule(args.development_schedule)

    # prepare the samples
    samples = prepare_samples(project_root=args.project_root, development_schedule=development_schedule)

    # generate docstrings for the nodes
    client = FluxOpenAIChat(
        cache_file=args.cache_file,
        base_url=args.base_url,
        api_key=args.api_key,
        max_qpm=args.max_qpm,
        max_retries=args.max_retries,
    )

    # collate the requests
    requests = [request_collate(sample, n_shots=2, model=args.model) for sample in samples]

    # collect the responses
    responses = client.request(requests)
    contents = [response.choices[0].message.content if response is not None else None for response in responses]

    docstrings = {}
    for sample, content in zip(samples, contents):
        if content is None:
            continue
        docstrings[sample['node-id']] = {'docstring': content, 'function-content': sample['function-content']}

    # save the docstrings
    with open(args.output_file, "w") as f:
        json.dump(docstrings, f, indent=4)

    print(f"Docstrings saved to `{args.output_file}`.")


if __name__ == "__main__":

    main()
