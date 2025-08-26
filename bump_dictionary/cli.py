from pathlib import Path

import typer
from typing_extensions import Annotated

from . import utils
from .logger import VerbosityLevel, configure_logger, log_error, logger
from .models import new_dictionary_model, old_dictionary_model

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
    old_dictionary_schema = (
        old_dictionary_model.DataDictionary.model_json_schema()
    )
    new_dictionary_schema = (
        new_dictionary_model.DataDictionary.model_json_schema()
    )

    current_dict = utils.load_json(data_dictionary)

    if not utils.get_validation_errors_for_schema(
        current_dict, new_dictionary_schema
    ):
        log_error(
            logger,
            "Data dictionary is already up-to-date with the latest schema.",
        )

    old_schema_validation_errs = utils.get_validation_errors_for_schema(
        current_dict, old_dictionary_schema
    )
    if old_schema_validation_errs:
        validation_errs = ""
        for error in old_schema_validation_errs:
            validation_errs += (
                " -> "
                + ".".join(map(str, error.path))
                + f": {error.message}\n"
            )
        log_error(
            logger,
            "The data dictionary is not valid against the previous schema and may be too outdated to upgrade automatically. "
            "Please re-annotate your dataset using the latest version of the annotation tool to continue.\n"
            f"Found {len(old_schema_validation_errs)} error(s):\n"
            f"{validation_errs}",
        )

    try:
        updated_dict = utils.encode_variable_type(current_dict)
        new_schema_validation_errs = utils.get_validation_errors_for_schema(
            updated_dict, new_dictionary_schema
        )
        if new_schema_validation_errs:
            validation_errs = ""
            for error in new_schema_validation_errs:
                validation_errs += (
                    " -> "
                    + ".".join(map(str, error.path))
                    + f": {error.message}\n"
                )
            log_error(
                logger,
                "Upgrading the data dictionary resulted in unexpected validation errors against the latest schema.\n"
                f"Found {len(new_schema_validation_errs)} error(s):\n"
                f"{validation_errs}",
            )
    except Exception as e:
        log_error(
            logger,
            f"An unexpected error occurred while upgrading the data dictionary: {e}",
        )

    utils.save_json(updated_dict, output, overwrite)

    logger.info(
        f"Successfully updated data dictionary. Output saved to {output}"
    )
