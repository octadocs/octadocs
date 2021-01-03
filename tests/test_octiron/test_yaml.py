from pathlib import Path

from rdflib import RDF, BNode, Literal, URIRef

from octadocs.octiron import Octiron
from octadocs.octiron.types import LOCAL, OCTA

LOCAL_IRI = URIRef('local:test.yaml')


def test_yaml():
    """Update Octiron graph from a YAML file."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'test.yaml',
        local_iri=LOCAL_IRI,
    )

    assert set(octiron.graph) == {
        (BNode('b0'), RDF.subject, Literal('s')),
        (BNode('b1'), RDF.predicate, Literal('p')),
        (BNode('b2'), RDF.object, Literal('o')),
        (LOCAL_IRI, RDF.type, OCTA.Page),
        (LOCAL_IRI, LOCAL.given, Literal('spo')),
        (LOCAL_IRI, LOCAL.infer, BNode('b0')),
        (LOCAL_IRI, LOCAL.infer, BNode('b1')),
        (LOCAL_IRI, LOCAL.infer, BNode('b2')),
    }
