# Bump Neurobagel data dictionaries

`bump-dictionary` is a tool to help migrate your existing Neurobagel data dictionaries to the latest data dictionary schema.


## Development environment

### Setting up a local development environment
1. Clone the repository

    ```bash
    git clone https://github.com/neurobagel/bump-dictionary.git
    cd bump-dictionary
    ```

2. Install the CLI and all development dependencies in editable mode:

    ```bash
    pip install -e ".[dev]"
    ```

Confirm that everything works well by running the tests: 
`pytest .`

### Setting up code formatting and linting (recommended)

[pre-commit](https://pre-commit.com/) is configured in the development environment for this repository, and can be set up to automatically run a number of code linters and formatters on any commit you make according to the consistent code style set for this project.

Run the following from the repository root to install the configured pre-commit "hooks" for your local clone of the repo:
```bash
pre-commit install
```

pre-commit will now run automatically whenever you run `git commit`.

### Updating dependencies
If new runtime or development dependencies are needed, add them to `pyproject.toml` using minimal version constraints.
