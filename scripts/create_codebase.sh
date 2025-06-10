#!/bin/bash

REPOSITORY=0b01001001/spectree
PROJECT_ROOT=outputs/workspace
DEVELOPMENT_SCHEDULE=outputs/$REPOSITORY/development-schedule.json
DOCSTRINGS=outputs/$REPOSITORY/docstrings.json

sweflow-create-codebase \
	--project-root $PROJECT_ROOT \
	--development-schedule $DEVELOPMENT_SCHEDULE \
	--docstrings $DOCSTRINGS \
	--temp-dir /tmp \
	--output-codebase-dir outputs/$REPOSITORY \
	--output-dir outputs/$REPOSITORY
