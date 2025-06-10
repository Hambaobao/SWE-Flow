# SWE-Flow

Let's take `0b01001001/spectree` as an example.

## STEP 0: Prepare
Start a docker container using the pre-built image `hambaobao/sweflow:0b01001001__--__spectree`. The `__--__` is the separator between the username and the repository name.
Then copy all files in the `/sweflow/sweflow-build/workspace.backup` to the `/workspace` directory.

## STEP 1: Trace Pytest
```bash
#!/bin/bash

REPOSITORY=0b01001001/spectree
MAX_WORKERS=8
MAX_TESTS=None
RANDOM=True
RANDOM_SEED=42

# clone the SWE-Flow-Trace repository
git clone https://github.com/Hambaobao/SWE-Flow-Trace.git /tmp/SWE-Flow-Trace

# install the SWE-Flow package
pip install -e /tmp/SWE-Flow-Trace

# run the trace
OUTPUT_DIR=/tmp/outputs/$REPOSITORY
sweflow-trace-python \
    --project-root /workspace \
    --max-workers $MAX_WORKERS \
    --max-tests $MAX_TESTS \
    --random $RANDOM \
    --random-seed $RANDOM_SEED \
    --output-dir $OUTPUT_DIR
```

This will generate a `tests-info.json` file and a `traces.json` file in the output directory.

## STEP 2: Schedule

```bash
#!/bin/bash

REPOSITORY=0b01001001/spectree
TRACE_FILE=/tmp/outputs/$REPOSITORY/traces.json
OUTPUT_DIR=/tmp/outputs/$REPOSITORY

sweflow-schedule-python --trace-file $TRACE_FILE --output-dir $OUTPUT_DIR
```
This will generate a `development-schedule.json` file and `dependency-graphs.json` file in the output directory.


## STEP 3: Create Docstrings

To create docstrings, you need to set up a local LLM server, then run the following command:

```bash
#!/bin/bash

REPOSITORY=0b01001001/spectree
PROJECT_ROOT=/workspace
DEVELOPMENT_SCHEDULE=/tmp/outputs/$REPOSITORY/development-schedule.json
CACHE_FILE=/tmp/outputs/$REPOSITORY/cache/docstrings.jsonl
OUTPUT_FILE=/tmp/outputs/$REPOSITORY/docstrings.json
BASE_URL=http://10.77.247.231:54513/v1
API_KEY=token-abc123
MODEL=qwen2.5-coder-32b-instruct
QPM=32

sweflow-create-docstring \
    --project-root $PROJECT_ROOT \
    --development-schedule $DEVELOPMENT_SCHEDULE \
    --base-url $BASE_URL \
    --api-key $API_KEY \
    --model $MODEL \
    --batch-size $QPM \
    --cache-file $CACHE_FILE \
    --output-file $OUTPUT_FILE

```

This will generate a `docstrings.json` file in the output directory.

## STEP 4: Create Specifications

To create specifications, you need to set up a local LLM server, then run the following command:

```bash
#!/bin/bash

REPOSITORY=0b01001001/spectree
PROJECT_ROOT=/workspace
DEVELOPMENT_SCHEDULE=/tmp/outputs/$REPOSITORY/development-schedule.json
CACHE_FILE=/tmp/outputs/$REPOSITORY/cache/specifications.jsonl
OUTPUT_FILE=/tmp/outputs/$REPOSITORY/specifications.json
BASE_URL=http://10.77.249.249:57627/v1
API_KEY=token-abc123
MODEL=Qwen3-14B
MAX_QPM=32

sweflow-create-specification \
    --project-root $PROJECT_ROOT \
    --development-schedule $DEVELOPMENT_SCHEDULE \
    --base-url $BASE_URL \
    --api-key $API_KEY \
    --model $MODEL \
    --max-qpm $MAX_QPM \
    --cache-file $CACHE_FILE \
    --output-file $OUTPUT_FILE

```

This will generate a `specifications.json` file in the output directory.


## STEP 5: Create Codebase

```bash
#!/bin/bash

REPOSITORY=0b01001001/spectree
PROJECT_ROOT=/workspace
DEVELOPMENT_SCHEDULE=/tmp/outputs/$REPOSITORY/development-schedule.json
DOCSTRINGS=/tmp/outputs/$REPOSITORY/docstrings.json
SPECIFICATIONS=/tmp/outputs/$REPOSITORY/specifications.json

sweflow-create-codebase \
	--project-root $PROJECT_ROOT \
	--development-schedule $DEVELOPMENT_SCHEDULE \
	--docstrings $DOCSTRINGS \
	--temp-dir /tmp \
	--output-codebase-dir /tmp/outputs/$REPOSITORY \
	--output-dir /tmp/outputs/$REPOSITORY

```

This will generate a `codebase.zip` file in the output directory.


## STEP 6: Merge Dataset

Finally, run the following command to merge the dataset:

```bash
#!/bin/bash

REPOSITORY=0b01001001/spectree
REPOSITORY_ID="${REPOSITORY//\//__--__}"
INPUT_DIR=data/origin/$REPOSITORY_ID/json
OUTPUT_FILE=data/origin/$REPOSITORY_ID/dataset.jsonl

python -m sweflow.utils.merge \
	--repository $REPOSITORY \
	--input-dir $INPUT_DIR \
	--output-file $OUTPUT_FILE

```

This will generate a `dataset.jsonl` file in the output directory, which contains:
- `instance_id`: the id of the problem instance
- `repo`: the repository name
- `problem_statement`: the problem statement
- `patch`: the patch to fix the problem
- `base_commit`: the SHA of the commit containing the code before applying any fix (i.e. the "buggy" or in-development version)
- `reference_commit`: the SHA of the commit generated after applying the ground-truth patch (i.e. the "fixed" version)
- `fail_to_pass`: the number of test cases that fail before and succeed after the patch is applied
- `pass_to_pass`: the number of test cases that pass before and pass after the patch is applied
