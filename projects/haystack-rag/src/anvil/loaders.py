from pathlib import Path
from typing import Any
import yaml
from haystack import Pipeline

def build_from_yaml(yaml_path: Path, overrides: dict[str, Any]) -> Pipeline:
    data = {**yaml.full_load(stream=yaml_path.open()), **overrides}
    pipeline = Pipeline.from_dict(data=data)
    return pipeline
