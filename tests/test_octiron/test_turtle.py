from pathlib import Path

from rdflib import RDFS, DC, Literal

from octadocs.octiron.plugins import TurtleLoader
from octadocs.octiron import Triple


def test_turtle():
    path = Path(__file__).parent / 'data/rdfs.ttl'

    stream = TurtleLoader(path=path).stream()

    assert next(stream) == Triple(
        RDFS.uri,
        DC.title,
        Literal('The RDF Schema vocabulary (RDFS)'),
    )
