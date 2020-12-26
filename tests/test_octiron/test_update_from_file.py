from pathlib import Path

from rdflib import URIRef, RDFS, DC, Literal, Graph

from octiron import Octiron


def test_turtle():
    """Update Octiron graph from a Turtle file."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'rdfs.ttl',
        iri=URIRef('local:rdfs.ttl'),
    )

    assert next(octiron.graph.quads()) == (
        RDFS.uri,
        DC.title,
        Literal('The RDF Schema vocabulary (RDFS)'),
        Graph(identifier=URIRef('local:rdfs.ttl')),
    )


def test_markdown():
    """Update Octiron graph from a Markdown file."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'test.md',
        iri=URIRef('local:test.md'),
    )

    assert next(octiron.graph.quads()) == (
        URIRef('local:test'),
        URIRef('local:title'),
        Literal('Hey, I am a test!'),
        Graph(identifier=URIRef('local:test.md')),
    )
