from pathlib import Path

from rdflib import DC, RDF, RDFS, Graph, Literal, URIRef

from octadocs.octiron import Octiron
from octadocs.octiron.types import OCTA

LOCAL_IRI = URIRef('local:test.md')


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
        local_iri=LOCAL_IRI,
    )

    assert set(octiron.graph.quads()) == {
        (
            URIRef('local:test'),
            URIRef('local:title'),
            Literal('Hey, I am a test!'),
            Graph(identifier=LOCAL_IRI),
        ),
        (
            URIRef('local:test'),
            OCTA.subjectOf,
            LOCAL_IRI,
            Graph(identifier=LOCAL_IRI),
        ),
        (
            LOCAL_IRI,
            RDF.type,
            OCTA.Page,
            Graph(identifier=LOCAL_IRI),
        ),
    }


def test_markdown_without_id():
    """Update Octiron graph from a Markdown file without a $id."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'test_without_id.md',
        local_iri=LOCAL_IRI,
    )

    assert set(octiron.graph.quads()) == {
        (
            LOCAL_IRI,
            URIRef('local:title'),
            Literal('Hey, I am a test!'),
            Graph(identifier=LOCAL_IRI),
        ),
        (
            LOCAL_IRI,
            RDF.type,
            OCTA.Page,
            Graph(identifier=LOCAL_IRI),
        ),
    }
