from pathlib import Path

import typer
from typing_extensions import Annotated

from . import utils
from .logger import log_error, logger
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
    ] = Path("bumped_dictionary.json"),
):
    current_dict = utils.load_json(data_dictionary)

    old_schema_validation_errs = utils.validate_against_dictionary_schema(
        current_dict, old_dictionary_model.DataDictionary.model_json_schema()
    )

    if old_schema_validation_errs:
        validation_errs = ""
        for error in old_schema_validation_errs:
            validation_errs += (
                " ->" + ".".join(map(str, error.path)) + f": {error.message}\n"
            )
        log_error(
            logger,
            "The data dictionary is not valid against the previous schema and may be too outdated to upgrade automatically. "
            "Please re-annotate your dataset using the latest version of the annotation tool to continue.\n"
            f"Found {len(old_schema_validation_errs)} error(s):\n"
            f"{validation_errs}",
        )

    new_schema_validation_errs = utils.validate_against_dictionary_schema(
        current_dict, new_dictionary_model.DataDictionary.model_json_schema()
    )

    if not new_schema_validation_errs:
        logger.info(
            "Data dictionary is already up-to-date with the latest schema."
        )
        raise typer.Exit(code=0)


if __name__ == "__main__":
    bump_dictionary()
