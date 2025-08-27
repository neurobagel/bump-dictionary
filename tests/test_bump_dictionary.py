import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from bump_dictionary.cli import bump_dictionary


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture(scope="session")
def example_dictionaries_path():
    return Path(__file__).absolute().parent / "data"


@pytest.fixture(scope="function")
def example_output_path(tmp_path):
    return tmp_path / "my_updated_dictionary.json"


@pytest.fixture(scope="session")
def load_test_json():
    def _read_file(file_path):
        with open(file_path, "r") as f:
            return json.load(f)

    return _read_file


def test_valid_legacy_dictionary_upgraded(
    load_test_json, example_dictionaries_path, runner, example_output_path
):
    """Test that a data dictionary valid against the previous schema is upgraded correctly."""
    target_dict = load_test_json(
        example_dictionaries_path / "latest_schema_dictionary.json"
    )

    result = runner.invoke(
        bump_dictionary,
        [
            str(example_dictionaries_path / "legacy_schema_dictionary.json"),
            str(example_output_path),
        ],
    )

    output = load_test_json(example_output_path)

    assert result.exit_code == 0
    assert output == target_dict


def test_valid_latest_dictionary_not_upgraded(
    example_dictionaries_path, runner, caplog
):
    """
    Test that a data dictionary valid against the latest schema is not upgraded,
    with an informative error.
    """
    result = runner.invoke(
        bump_dictionary,
        [
            str(example_dictionaries_path / "latest_schema_dictionary.json"),
            str(example_output_path),
        ],
    )

    assert result.exit_code != 0
    assert len(caplog.records) == 1
    assert "already up-to-date" in caplog.text


def test_invalid_dictionary_not_upgraded(
    example_dictionaries_path, runner, caplog
):
    """
    Test that a data dictionary which is not valid against the previous schema is not upgraded,
    with an informative error.
    """
    result = runner.invoke(
        bump_dictionary,
        [
            str(example_dictionaries_path / "invalid_dictionary.json"),
            str(example_output_path),
        ],
    )

    assert result.exit_code != 0
    assert len(caplog.records) == 1
    assert "not valid against the previous schema" in caplog.text
    assert "2 error(s)" in caplog.text
