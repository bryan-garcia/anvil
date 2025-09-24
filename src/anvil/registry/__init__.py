import os
from pathlib import Path
from anvil.registry.types import Entry


def _default_home() -> Path:
    env = os.getenv("ANVIL_HOME")
    if env:
        return Path(env)
    # try git root
    p = Path.cwd()
    for parent in (p, *p.parents):
        if (parent / ".git").exists():
            return parent / ".anvil"
    return Path.home() / ".anvil"


_REGDIR = _default_home()
_REGFILE = _REGDIR / "registry.yaml"
# In-memory registry for the current process
_REG: dict[str, Entry] = {}
