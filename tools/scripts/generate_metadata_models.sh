#!/usr/bin/env bash

source tools/scripts/generate_models.sh

TMP_DIR=$(mktemp -d)
SCHEMA_DIR="metadata/schemas/"
GEN_DIR_NAME="metadata_models"

copy_schemas $TMP_DIR $SCHEMA_DIR
generate_models $TMP_DIR $GEN_DIR_NAME