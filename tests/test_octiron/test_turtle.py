from pathlib import Path

from octadocs.octiron import Octiron
from octadocs.octiron.plugins import TurtleLoader
from octadocs.octiron.types import Triple
from rdflib import DC, RDFS, Graph, Literal, URIRef

LOCAL_IRI = URIRef('local:test.md')


def test_turtle_loader():
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


def test_turtle():
    """Update Octiron graph from a Turtle file."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'rdfs.ttl',
        local_iri=URIRef('local:rdfs.ttl'),
    )

    assert next(octiron.graph.quads()) == (
        RDFS.uri,
        DC.title,
        Literal('The RDF Schema vocabulary (RDFS)'),
        Graph(identifier=URIRef('local:rdfs.ttl')),
    )
