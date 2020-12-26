from pathlib import Path
from typing import Iterator

import rdflib

from octiron.types import Triple, Context


class Loader:
    """Data importer for Octiron."""

    # Which files is this loader working with?
    regex: str

    # Absolute path to source file
    path: Path

    # Local address of the file, which will be used as graph name
    local_iri: rdflib.URIRef

    # JSON-LD context
    context: Context

    def __init__(
        self,
        path: Path,
        local_iri: rdflib.URIRef,
        context: Context,
    ) -> None:
        """Initialize the data loader."""
        self.path = path
        self.context = context
        self.local_iri = local_iri

    def stream(self) -> Iterator[Triple]:
        """Read the source data and return a stream of triples."""
        raise NotImplementedError()
