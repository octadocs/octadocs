import json
from pathlib import Path

import yaml
from octadocs.octiron.yaml_extensions import convert_dollar_signs
from octadocs.types import Context


def context_from_json(path: Path) -> Context:
    """Load context.json file and return its content."""
    with path.open('r') as context_file:
        return json.load(context_file)


def context_from_yaml(path: Path) -> Context:
    """Load context.json file and return its content."""
    with path.open('r') as context_file:
        raw_data = yaml.load(context_file, Loader=yaml.SafeLoader)
        return convert_dollar_signs(raw_data)
