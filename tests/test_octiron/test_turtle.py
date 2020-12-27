from pathlib import Path

from rdflib import DC, RDFS, Literal, URIRef

from octadocs.octiron.plugins import TurtleLoader
from octadocs.octiron.types import Triple


def test_turtle():
    path = Path(__file__).parent / 'data/rdfs.ttl'

    stream = TurtleLoader(
        path=path,
        context={},
        local_iri=URIRef('local:rdfs.ttl'),
        global_url='/rdfs',
    ).stream()

    assert next(stream) == Triple(
        RDFS.uri,
        DC.title,
        Literal('The RDF Schema vocabulary (RDFS)'),
    )
