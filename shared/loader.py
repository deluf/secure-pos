import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

def load_and_validate_json_file(path: str, schema: dict):
    """
    Load config JSON from disk, validate it against the provided schema,
    and return the parsed dictionary.
    """
    # Load JSON
    with open(path, "r") as f:
        config_data = json.load(f)

    # Validate JSON
    try:
        validate(instance=config_data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Invalid configuration file '{path}': {e.message}")

    return config_data
