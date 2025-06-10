#!/bin/bash

REPOSITORY=0b01001001/spectree
REPOSITORY_ID="${REPOSITORY//\//__--__}"
INPUT_DIR=data/origin/$REPOSITORY_ID/json
OUTPUT_FILE=data/origin/$REPOSITORY_ID/dataset.jsonl

python -m sweflow.utils.merge \
	--repository $REPOSITORY \
	--input-dir $INPUT_DIR \
	--output-file $OUTPUT_FILE
