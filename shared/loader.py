import json
from jsonschema import validate, ValidationError


def load_and_validate_json_file(json_path: str, schema_path: str):
    # Load JSON data file
    with open(json_path, "r") as f:
        config_data = json.load(f)

    # Load JSON schema file
    with open(schema_path, "r") as f:
        schema = json.load(f)

    # Validate JSON
    try:
        validate(instance=config_data, schema=schema)
    except ValidationError as e:
        raise ValueError(
            f"Invalid configuration file '{json_path}': {e.message}"
        ) from e

    return config_data
