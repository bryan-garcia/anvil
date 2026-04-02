import yaml
from pathlib import Path
import importlib
import importlib.util
from typing import Callable
from anvil.registry import _REG, _REGFILE, _REGDIR
from anvil.registry.types import Entry, YamlEntry, PyEntry
from anvil.utils import _normalize_name, _abs


def _load_persisted() -> None:
    """Load YAML-registered entries into _REG (idempotent)."""
    if not _REGFILE.exists():
        return
    data = yaml.safe_load(_REGFILE.read_text()) or {}
    # Data layout: { name: {"file_path": "<abs path>"} }
    for name, meta in data.items():
        fp = meta.get("file_path")
        if fp:
            _REG.setdefault(name, YamlEntry(file_path=fp))


def _persist_yaml_entries() -> None:
    """Write only YAML entries back to disk (Python entries are runtime-only)."""
    _REGDIR.mkdir(parents=True, exist_ok=True)
    data = {
        name: {"file_path": entry.file_path}
        for name, entry in _REG.items()
        if isinstance(entry, YamlEntry)
    }
    # Make it deterministic for nicer diffs
    _REGFILE.write_text(yaml.safe_dump(dict(sorted(data.items())), sort_keys=True))




def register(name: str):
    """
    Decorator for Python builders.

    Usage:
        @register("rag/query/simple")
        def build(...)-> haystack.Pipeline: ...
    """
    norm = _normalize_name(name)

    def deco(fn: Callable):
        import_path = f"{fn.__module__}:{fn.__name__}"
        _REG[norm] = PyEntry(import_path=import_path)
        return fn

    return deco


def register_yaml(name: str, file_path: str) -> None:
    """
    Register a serialized pipeline YAML under a name.
    Persists to .anvil/registry.yaml
    """
    norm = _normalize_name(name)
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Cannot register '{name}': file not found: {file_path}"
        )
    _load_persisted()
    _REG[norm] = YamlEntry(file_path=_abs(path))
    _persist_yaml_entries()


def import_module_file(path: Path):
    """
    Import a local .py file so any @register decorators execute.
    Returns the loaded module.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot import {path}")
    mod = importlib.util.module_from_spec(spec)
    import sys as _sys

    _sys.modules[path.stem] = mod
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def list_entries() -> dict[str, str]:
    """Return {name: ref} for both Python and YAML entries."""
    _load_persisted()
    out: dict[str, str] = {}
    for name, entry in _REG.items():
        if isinstance(entry, PyEntry):
            out[name] = entry.import_path
        else:
            out[name] = entry.file_path
    return dict(sorted(out.items()))


def get_entry(name: str) -> Entry:
    _load_persisted()
    norm = _normalize_name(name)
    if norm not in _REG:
        raise KeyError(
            f"Pipeline '{name}' not found. Use 'anvil list' or 'anvil register'."
        )
    return _REG[norm]

def del_entry(name: str) -> None:
    _load_persisted()
    norm = _normalize_name(name)
    if norm not in _REG:
        raise KeyError(
            f"Pipeline '{name}' not found. Use 'anvil list' or 'anvil register'."
        )
    del _REG[norm]
    _persist_yaml_entries()


def resolve_builder(name: str) -> Callable[..., object]:
    """
    Return a callable that, when invoked, builds a Haystack Pipeline.

    For PyEntry: import the module and return the function.
    For YamlEntry: return a lambda that calls loaders.build_from_yaml(abs_path, overrides).
    """
    entry = get_entry(name)
    if isinstance(entry, PyEntry):
        module, func = entry.import_path.split(":")
        builder = getattr(importlib.import_module(module), func)
        return builder  # expected signature: (**kwargs) -> haystack.Pipeline
    else:
        from ..loaders import build_from_yaml

        yaml_path = Path(entry.file_path)

        def _builder(**overrides):
            return build_from_yaml(yaml_path, overrides)

        return _builder


def show_entry(name: str) -> dict:
    """Structured info for CLI 'show' (easy to JSON-ify)."""
    e = get_entry(name)
    kind = "python" if isinstance(e, PyEntry) else "yaml"
    ref = e.import_path if isinstance(e, PyEntry) else e.file_path
    return {"name": name, "kind": kind, "ref": ref}
