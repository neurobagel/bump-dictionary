import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from bump_dictionary.cli import bump_dictionary


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


@pytest.fixture(scope="session")
def test_data():
    return Path(__file__).absolute().parent / "data"


@pytest.fixture(scope="session")
def load_test_json():
    def _read_file(file_path):
        with open(file_path, "r") as f:
            return json.load(f)

    return _read_file


def test_valid_old_dictionary_upgraded(
    load_test_json, test_data, runner, tmp_path
):
    target_dict = load_test_json(test_data / "new_dictionary.json")
    output_path = tmp_path / "my_updated_dictionary.json"

    result = runner.invoke(
        bump_dictionary,
        [str(test_data / "old_dictionary.json"), str(output_path)],
    )

    output = load_test_json(output_path)

    assert result.exit_code == 0
    assert output == target_dict


def test_valid_new_dictionary_unchanged(
    load_test_json, test_data, runner, tmp_path, caplog
):
    result = runner.invoke(
        bump_dictionary, [str(test_data / "new_dictionary.json")]
    )

    assert result.exit_code != 0
    assert len(caplog.records) == 1
    assert "already up-to-date" in caplog.text


def test_invalid_dictionary_errors_out(
    load_test_json, test_data, runner, tmp_path, caplog
):
    result = runner.invoke(
        bump_dictionary, [str(test_data / "invalid_dictionary.json")]
    )

    assert result.exit_code != 0
    assert len(caplog.records) == 1
    assert "not valid against the previous schema" in caplog.text
    assert "2 error(s)" in caplog.text
