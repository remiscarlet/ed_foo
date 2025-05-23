#!/usr/bin/env bash

function copy_schemas {
    TMP_DIR=${1}
    IN_DIR=${2}

    mkdir -p $TMP_DIR
    cp ${IN_DIR}*.json ${TMP_DIR}
}

function get_hw_type {
    if [[ $(uname -s) == "Darwin" ]];
    then
        echo "mac"
    else
        echo "linux"
    fi
}


function generate_models {
    TMP_DIR=${1}

    GEN_DIR=src/gen/
    OUT_DIR=${GEN_DIR}${2}/

    mkdir -p ${GEN_DIR}
    mkdir -p ${OUT_DIR}
    poetry run datamodel-codegen \
        --reuse-model \
        --strict-nullable \
        --input-file-type jsonschema \
        --input ${TMP_DIR} \
        --output-model-type pydantic_v2.BaseModel \
        --output ${OUT_DIR}

    touch ${GEN_DIR}__init__.py
    touch ${OUT_DIR}__init__.py

    # The `__future__ import annotations` forward references resolve certain types to a NoneType, causing
    # pydantic to resolve fields like `list[StationEconomy]` to `list[NoneType]` at runtime
    if [[ $(get_hw_type) == 'mac' ]];
    then
        find ${OUT_DIR} -type f -exec sed -i '' "s/from __future__ import annotations//g" {} \;
    else
        find ${OUT_DIR} -type f -exec sed -i "s/from __future__ import annotations//g" {} \;
    fi

    rm -rf $TMP_DIR
}