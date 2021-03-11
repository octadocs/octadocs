from pathlib import Path

from octadocs.octiron import Octiron
from octadocs.octiron.types import LOCAL, OCTA
from rdflib import RDF, RDFS, Graph, Literal, URIRef

LOCAL_IRI = URIRef('local:test.md')


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


def test_markdown_with_context():
    """Update Octiron graph from a Markdown file with a $context."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'test_with_context.md',
        local_iri=LOCAL_IRI,
    )

    assert set(octiron.graph.quads()) == {
        (
            LOCAL_IRI,
            RDFS.label,
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


def test_markdown_with_dollar_sign():
    """Update Octiron graph from a Markdown file with a $context."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'test_dollar_id.md',
        local_iri=LOCAL_IRI,
    )

    assert set(octiron.graph.quads()) == {
        (
            LOCAL_IRI,
            RDFS.label,
            Literal('Hey, I am a test!'),
            Graph(identifier=LOCAL_IRI),
        ),
        (
            LOCAL_IRI,
            RDFS.domain,
            LOCAL.UnitTesting,
            Graph(identifier=LOCAL_IRI),
        ),
        (
            LOCAL_IRI,
            RDF.type,
            OCTA.Page,
            Graph(identifier=LOCAL_IRI),
        ),
    }
