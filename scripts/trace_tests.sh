#!/bin/bash

REPOSITORY=0b01001001/spectree
MAX_WORKERS=1
MAX_TESTS=None
RANDOM=False
RANDOM_SEED=42

# run the trace
OUTPUT_DIR=outputs/$REPOSITORY
sweflow-trace-python \
    --project-root /workspace \
    --max-workers $MAX_WORKERS \
    --max-tests $MAX_TESTS \
    --random $RANDOM \
    --random-seed $RANDOM_SEED \
    --output-dir $OUTPUT_DIR