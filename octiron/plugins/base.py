from pathlib import Path
from typing import Iterator

from octiron.types import Triple, Context


class Loader:
    """Data importer for Octiron."""

    # Which files is this loader working with?
    regex: str

    # Absolute path to source file
    path: Path

    # JSON-LD context
    context: Context

    def __init__(self, path: Path, context: Context) -> None:
        """Initialize the data loader."""
        self.path = path
        self.context = context

    def stream(self) -> Iterator[Triple]:
        """Read the source data and return a stream of triples."""
        raise NotImplementedError()
