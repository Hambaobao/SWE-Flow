#!/bin/bash

REPOSITORY=0b01001001/spectree
PROJECT_ROOT=outputs/workspace
DEVELOPMENT_SCHEDULE=outputs/$REPOSITORY/development-schedule.json
CACHE_FILE=outputs/$REPOSITORY/cache/docstrings.jsonl
OUTPUT_FILE=outputs/$REPOSITORY/docstrings.json
BASE_URL=http://10.77.249.249:57627/v1
API_KEY=token-abc123
MODEL=Qwen3-14B
MAX_QPM=32

sweflow-create-docstring \
    --project-root $PROJECT_ROOT \
    --development-schedule $DEVELOPMENT_SCHEDULE \
    --base-url $BASE_URL \
    --api-key $API_KEY \
    --model $MODEL \
    --max-qpm $MAX_QPM \
    --cache-file $CACHE_FILE \
    --output-file $OUTPUT_FILE
