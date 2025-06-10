#!/bin/bash

REPOSITORY=0b01001001/spectree
TRACE_FILE=outputs/$REPOSITORY/traces.json
OUTPUT_DIR=outputs/$REPOSITORY

sweflow-schedule-python --trace-file $TRACE_FILE --output-dir $OUTPUT_DIR
