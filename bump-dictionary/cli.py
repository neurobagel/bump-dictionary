from pathlib import Path

import typer
import utils
from typing_extensions import Annotated

bump_dictionary = typer.Typer(
    help="Bump Neurobagel data dictionaries to the latest version of the data dictionary schema.",
    # context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
)


def main(
    data_dictionary: Annotated[
        Path,
        typer.Argument(help="Path to a Neurobagel data dictionary JSON file."),
    ],
    output: Annotated[
        Path, typer.Argument(help="Path to save the output JSON file.")
    ] = Path("bumped_dictionary.json"),
):
    utils.load_json(data_dictionary)


if __name__ == "__main__":
    typer.run(main)
