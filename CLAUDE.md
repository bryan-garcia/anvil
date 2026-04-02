# Anvil - Claude Code Sandbox

## What is this repo?

A sandbox for experiments, prototypes, and debugging. Projects are independent
of each other. There is no shared build system or deployment pipeline.

## Repository structure

- `projects/` - All experiments live here. Each subdirectory is self-contained.
- Each project has its own README.md describing what it is and how to run it.

## Conventions

- **New project**: Create a directory under `projects/` with a descriptive
  kebab-case name. Add a `README.md` explaining the project's purpose.
- **Python projects**: Use `uv` for dependency management. Each project gets
  its own virtual environment (`.venv` inside the project directory).
  Use `pyproject.toml` for dependencies.
- **Other languages**: Use that language's standard tooling.
- **No cross-project dependencies**: Projects must not import from each other.

## Starting a new Python project

```bash
mkdir -p projects/my-project
cd projects/my-project
uv init
uv venv
# start coding
```

## Working on an existing project

```bash
cd projects/<name>
cat README.md          # understand what it is
uv venv                # create venv if it doesn't exist
uv pip install -e .    # install dependencies
```

## Important notes

- Each project is isolated. Breaking one should never affect another.
- There is no repo-wide test suite or linting. Each project manages its own.
- The `.python-version` file at the root sets the default to 3.11.
