import json
from pathlib import Path
from typing import Any

import typer
import yaml


def dumps_json(data: dict[str, Any], **kwargs) -> str:
    """
    Serialize a dictionary to a JSON-formatted string with indentation.

    Args:
        data (dict[str, Any]): The data to serialize.
        **kwargs: Additional keyword arguments to pass to json.dumps.

    Returns:
        str: The JSON-formatted string.
    """
    return json.dumps(obj=data, indent=2, **kwargs)

def load_yaml(fpath: str | Path) -> dict[str, any]:
    """
    Load a YAML file and return its contents as a dictionary.

    Args:
        fpath (str | Path): Path to the YAML file.

    Returns:
        dict[str, any]: The loaded YAML data.
    """
    fpath = Path(fpath)
    return yaml.safe_load(stream=fpath.read_bytes())

def _echo_err(msg: str, code: int = 1) -> None:
    """
    Print an error message in red and exit the program with the given code.

    Args:
        msg (str): The error message to display.
        code (int, optional): The exit code. Defaults to 1.

    Raises:
        typer.Exit: Exits the program with the specified code.
    """
    typer.secho(msg, err=True, fg=typer.colors.RED)
    raise typer.Exit(code)

def _normalize_name(name: str) -> str:
    """
    Normalize a name string by stripping whitespace.

    Args:
        name (str): The name to normalize.

    Returns:
        str: The normalized name.
    """
    #
    # Simple normalization (future: enforce namespace/<name>@ver)
    #
    return name.strip()


def _abs(p: Path) -> str:
    """
    Return the absolute path as a string.

    Args:
        p (Path): The path to resolve.

    Returns:
        str: The absolute path as a string.
    """
    return str(p.resolve())
