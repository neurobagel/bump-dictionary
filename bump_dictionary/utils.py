import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .logger import log_error, logger


def load_json(file: Path) -> Any:
    """Load a JSON file and return its content if file has valid encoding and is valid JSON."""
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        log_error(
            logger,
            f"Data dictionary must have UTF-8 encoding: {file}. "
            "Tip: Need help converting your file? Try a tool like iconv (http://linux.die.net/man/1/iconv) or https://www.freeformatter.com/convert-file-encoding.html.",
        )
    except json.JSONDecodeError:
        log_error(
            logger,
            f"Data dictionary is not valid JSON: {file}.",
        )


def validate_against_dictionary_schema(
    data_dictionary: dict, schema: dict
) -> list:
    """
    Validate the data dictionary against a given schema and return all validation errors if any found.
    """
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(data_dictionary))
    return errors
