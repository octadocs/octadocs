from pathlib import Path

from octadocs.octiron import Octiron
from octadocs.types import LOCAL, OCTA
from rdflib import RDF, BNode, Literal, URIRef

LOCAL_IRI = URIRef('local:test.yaml')


def test_clear_named_graph():
    """Update Octiron graph from a YAML file."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'test.yaml',
        local_iri=LOCAL_IRI,
    )

    assert set(octiron.graph) == {
        (BNode(f'{LOCAL_IRI}/b0'), RDF.subject, Literal('s')),
        (BNode(f'{LOCAL_IRI}/b1'), RDF.predicate, Literal('p')),
        (BNode(f'{LOCAL_IRI}/b2'), RDF.object, Literal('o')),
        (LOCAL_IRI, RDF.type, OCTA.Page),
        (LOCAL_IRI, LOCAL.given, Literal('spo')),
        (LOCAL_IRI, LOCAL.infer, BNode(f'{LOCAL_IRI}/b0')),
        (LOCAL_IRI, LOCAL.infer, BNode(f'{LOCAL_IRI}/b1')),
        (LOCAL_IRI, LOCAL.infer, BNode(f'{LOCAL_IRI}/b2')),
    }

    octiron.clear_named_graph(
        local_iri=LOCAL_IRI,
    )

    assert not list(octiron.graph)
