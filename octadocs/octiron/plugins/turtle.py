from itertools import starmap
from typing import Iterator

import rdflib
from octadocs.octiron.plugins import Loader
from octadocs.types import Triple


class TurtleLoader(Loader):
    """Read data from Turtle files."""

    regex = r'\.ttl$'

    def stream(self) -> Iterator[Triple]:
        """Read a Turtle file and return a stream of triples."""
        graph = rdflib.Graph()
        graph.parse(source=str(self.path), format='turtle')
        return starmap(Triple, iter(graph))
