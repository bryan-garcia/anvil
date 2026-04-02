from typing import Union
from dataclasses import dataclass

@dataclass
class PyEntry:
    """A Python builder: import path 'package.module:func'."""

    import_path: str


@dataclass
class YamlEntry:
    """A serialized Haystack pipeline YAML file path."""

    file_path: str  # absolute or project-relative, we’ll normalize to abs on write

Entry = Union[PyEntry, YamlEntry]