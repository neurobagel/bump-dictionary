import json
from pathlib import Path
from typing import Any, Type

import typer
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from .logger import log_error, logger
from .models.old_dictionary_model import (
    CategoricalNeurobagel,
    ContinuousNeurobagel,
    IdentifierNeurobagel,
    Neurobagel,
    ToolNeurobagel,
)


def load_json(file: Path) -> Any:
    """Load a JSON file and return its content if file has valid encoding and is valid JSON."""
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except UnicodeDecodeError:
        log_error(
            logger,
            f"Data dictionary must have UTF-8 encoding: {file}. "
            "[italic]TIP: Need help converting your file? Try a tool like iconv (http://linux.die.net/man/1/iconv) or https://www.freeformatter.com/convert-file-encoding.html.[/italic]",
        )
    except json.JSONDecodeError:
        log_error(
            logger,
            f"Data dictionary is not valid JSON: {file}.",
        )


def save_json(data: dict, file: Path, overwrite: bool):
    """Save a dictionary as a JSON file."""
    if file.exists() and not overwrite:
        raise typer.Exit(
            typer.style(
                f"Output file {file} already exists. Use --overwrite or -f to overwrite.",
                fg=typer.colors.RED,
            )
        )

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_validation_errors_for_schema(
    data_dictionary: dict, schema: dict
) -> list:
    """
    Validate the data dictionary against a given schema and return all validation errors if any found.
    """
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(data_dictionary))
    return errors


def is_valid_annotated_column(
    annotations: dict, column_type: Type[Neurobagel]
) -> bool:
    """Validate the annotations against the given column type."""
    try:
        column_type.model_validate(annotations)
        return True
    except ValidationError:
        return False


def encode_variable_type(data_dictionary: dict) -> dict:
    """Remove 'Identifies' from annotations and add 'VariableType'."""
    variable_type_mapping = {
        IdentifierNeurobagel: "Identifier",
        CategoricalNeurobagel: "Categorical",
        ContinuousNeurobagel: "Continuous",
        ToolNeurobagel: "Collection",
    }

    for col in data_dictionary.values():
        if "Annotations" in col:
            col_annotations = col["Annotations"]
            for (
                neurobagel_type,
                variable_type,
            ) in variable_type_mapping.items():
                if is_valid_annotated_column(col_annotations, neurobagel_type):
                    col_annotations.pop("Identifies", None)
                    col_annotations["VariableType"] = variable_type
                    break
    return data_dictionary
