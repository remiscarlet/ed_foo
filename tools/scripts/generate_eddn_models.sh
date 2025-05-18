TMP_DIR=$(mktemp -d)

cp data/eddn/schemas/*.json ${TMP_DIR}

mkdir -p gen
poetry run datamodel-codegen \
    --reuse-model \
    --strict-nullable \
    --input-file-type jsonschema \
    --input ${TMP_DIR} \
    --output-model-type pydantic_v2.BaseModel \
    --output gen/eddn_models/

touch gen/__init__.py
touch gen/eddn_models/__init__.py

# The `__future__ import annotations` forward references resolve certain types to a NoneType, causing
# pydantic to resolve fields like `list[StationEconomy]` to `list[NoneType]` at runtime
find gen/eddn_models/ -type f -exec sed -i '' "s/from __future__ import annotations//g" {} \;

rm -rf $TMP_DIR