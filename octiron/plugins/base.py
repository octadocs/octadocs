from pathlib import Path
from typing import Iterable

from octiron.types import Triple


class OctironPlugin:
    """Data importer for Octiron."""

    regex: str
    path: Path

    def __init__(self, path: Path) -> None:
        """Initialize the plugin."""
        self.path = path

    def stream(self) -> Iterable[Triple]:
        """Read the source data and return a stream of triples."""
        raise NotImplementedError()
