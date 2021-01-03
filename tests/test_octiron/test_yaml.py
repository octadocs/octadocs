from pathlib import Path

from rdflib import DC, RDFS, Graph, Literal, URIRef, BNode, RDF

from octadocs.octiron import Octiron
from octadocs.octiron.plugins import TurtleLoader
from octadocs.octiron.types import Triple, OCTA, LOCAL

LOCAL_IRI = URIRef('local:test.md')


def test_yaml():
    """Update Octiron graph from a YAML file."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)

    octiron.update_from_file(
        path=data_dir / 'test.yaml',
        local_iri=URIRef('local:test.yaml'),
    )

    assert set(octiron.graph) == {
        (BNode('b0'), RDF.subject, Literal('s')),
        (BNode('b1'), RDF.predicate, Literal('p')),
        (BNode('b2'), RDF.object, Literal('o')),
        (URIRef('local:test.yaml'), RDF.type, OCTA.Page),
        (URIRef('local:test.yaml'), LOCAL.given, Literal('spo')),
        (URIRef('local:test.yaml'), LOCAL.infer, BNode('b0')),
        (URIRef('local:test.yaml'), LOCAL.infer, BNode('b1')),
        (URIRef('local:test.yaml'), LOCAL.infer, BNode('b2')),
    }
