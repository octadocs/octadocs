from pathlib import Path
from typing import Iterator

from octiron.types import Triple


class Loader:
    """Data importer for Octiron."""

    regex: str
    path: Path

    def __init__(self, path: Path) -> None:
        """Initialize the plugin."""
        self.path = path

    def stream(self) -> Iterator[Triple]:
        """Read the source data and return a stream of triples."""
        raise NotImplementedError()
