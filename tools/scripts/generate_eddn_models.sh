source tools/scripts/generate_models.sh

TMP_DIR=$(mktemp -d)/
SCHEMA_DIR="data/eddn/schemas/"
GEN_DIR_NAME="eddn_models"

copy_schemas $TMP_DIR $SCHEMA_DIR

# Add additional fields to journal-v1.0's Faction object
ORIG=journal-v1.0.json
TMP=journal-v1.0.tmp.json
mv ${TMP_DIR}${ORIG} ${TMP_DIR}${TMP}
jq '
  .properties.message.properties.Factions.items.properties += {
    "Allegiance": { "type": "string" },
    "FactionState": { "type": "string" },
    "Government": { "type": "string" },
    "Happiness": { "type": "string" },
    "Influence": { "type": "number" },
    "Name": { "type": "string" },
    "ActiveStates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["State"],
        "properties": {
          "State": { "type": "string" }
        }
      }
    },
    "RecoveringStates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["State"],
        "properties": {
          "State": { "type": "string" }
        }
      }
    },
    "PendingStates": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["State"],
        "properties": {
          "State": { "type": "string" }
        }
      }
    },
  }
' ${TMP_DIR}${TMP} > ${TMP_DIR}${ORIG}
rm ${TMP_DIR}${TMP}

generate_models $TMP_DIR $GEN_DIR_NAME