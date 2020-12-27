from pathlib import Path

from rdflib import URIRef, RDFS, DC, Literal, Graph, RDF

from octadocs.octiron import Octiron
from octadocs.octiron import OCTA


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


def test_markdown():
    """Update Octiron graph from a Markdown file."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'test.md',
        local_iri=URIRef('local:test.md'),
    )

    assert set(octiron.graph.quads()) == {
        (
            URIRef('local:test'),
            URIRef('local:title'),
            Literal('Hey, I am a test!'),
            Graph(identifier=URIRef('local:test.md')),
        ),
        (
            URIRef('local:test'),
            OCTA.subjectOf,
            URIRef('local:test.md'),
            Graph(identifier=URIRef('local:test.md')),
        ),
        (
            URIRef('local:test.md'),
            RDF.type,
            OCTA.Page,
            Graph(identifier=URIRef('local:test.md')),
        ),
    }


def test_markdown_without_id():
    """Update Octiron graph from a Markdown file without a $id."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'test_without_id.md',
        local_iri=URIRef('local:test.md'),
    )

    assert set(octiron.graph.quads()) == {
        (
            URIRef('local:test.md'),
            URIRef('local:title'),
            Literal('Hey, I am a test!'),
            Graph(identifier=URIRef('local:test.md')),
        ),
        (
            URIRef('local:test.md'),
            RDF.type,
            OCTA.Page,
            Graph(identifier=URIRef('local:test.md')),
        ),
    }
