import json
from pathlib import Path

import typer
from typing_extensions import Annotated

from . import utils
from .logger import VerbosityLevel, configure_logger, log_error, logger
from .models import latest_dictionary_model, legacy_dictionary_model

bump_dictionary = typer.Typer(
    help="Bump Neurobagel data dictionaries to the latest version of the data dictionary schema.",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
)


@bump_dictionary.command()
def main(
    data_dictionary: Annotated[
        Path,
        typer.Argument(help="Path to a Neurobagel data dictionary JSON file."),
    ],
    output: Annotated[
        Path, typer.Argument(help="Path to save the output JSON file.")
    ] = Path("updated_dictionary.json"),
    verbosity: Annotated[
        VerbosityLevel,
        typer.Option(
            "--verbosity",
            "-v",
            callback=configure_logger,
            help="Set the verbosity level of the output. 0 = show errors only; 1 = show errors, warnings, and informational messages; 3 = show all logs, including debug messages.",
        ),
    ] = VerbosityLevel.INFO,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            "-f",
            help="Overwrite the output file if it already exists.",
        ),
    ] = False,
):
    utils.check_overwrite(output, overwrite)

    legacy_dictionary_schema = (
        utils.patch_schema_to_allow_transformation_or_format(
            legacy_dictionary_model.DataDictionary.model_json_schema()
        )
    )
    latest_dictionary_schema = (
        latest_dictionary_model.DataDictionary.model_json_schema()
    )

    current_dict = utils.load_json(data_dictionary)

    if not utils.get_validation_errors_for_schema(
        current_dict, latest_dictionary_schema
    ):
        log_error(
            logger,
            "Data dictionary is already up-to-date with the latest schema.",
        )

    legacy_schema_validation_errs = utils.get_validation_errors_for_schema(
        current_dict, legacy_dictionary_schema
    )
    if legacy_schema_validation_errs:
        validation_errs = ""
        for error in legacy_schema_validation_errs:
            validation_errs += (
                " -> "
                + ".".join(map(str, error.path))
                + f": {error.message}\n"
            )
        log_error(
            logger,
            "The data dictionary is not valid against the previous schema and may be too outdated to upgrade automatically. "
            "Please re-annotate your dataset using the latest version of the annotation tool to continue.\n"
            f"Found {len(legacy_schema_validation_errs)} error(s):\n"
            f"{validation_errs}",
        )

    updated_dict = utils.convert_transformation_to_format(current_dict)
    updated_dict = utils.encode_variable_type(updated_dict)

    latest_schema_validation_errs = utils.get_validation_errors_for_schema(
        updated_dict, latest_dictionary_schema
    )
    if latest_schema_validation_errs:
        validation_errs = ""
        for error in latest_schema_validation_errs:
            validation_errs += (
                " -> "
                + ".".join(map(str, error.path))
                + f": {error.message}\n"
            )
        log_error(
            logger,
            "Unexpected validation errors occurred after upgrading the data dictionary to the latest schema.\n"
            f"Found {len(latest_schema_validation_errs)} error(s):\n"
            f"{validation_errs}"
            "Something likely went wrong in the upgrade process on our side. "
            "Please open an issue in https://github.com/neurobagel/bump-dictionary/issues.",
        )

    with open(output, "w", encoding="utf-8") as f:
        json.dump(updated_dict, f, ensure_ascii=False, indent=2)

    logger.info(
        f"Successfully updated data dictionary. Output saved to {output}"
    )
