"""
Test import JSON-LD documents with different IRI schemes.

Supplementary material for:

    https://github.com/RDFLib/rdflib-jsonld/issues/101
"""
import json

import rdflib
from rdflib import RDF


def test_jsonld_import_with_slashes():
    """
    Import a JSON-LD document with local:// IRIs.

    Strangely, after import, trailing slashes are added to these IRIs. This is
    quite unexpected.
    """
    source_document = {
        '@context': {
            'title': 'local://title',
        },
        '@id': 'local://boo',
        '@type': 'local://Foo',
        'title': 'Buzinga!',
    }

    graph = rdflib.Graph()
    graph.parse(
        data=json.dumps(source_document),
        format='json-ld',
    )

    assert set(graph) == {
        (
            # Like in here.
            rdflib.term.URIRef('local://boo/'),
            rdflib.term.URIRef('local://title'),
            rdflib.term.Literal('Buzinga!'),
        ),
        (
            rdflib.term.URIRef('local://boo/'),
            RDF.type,
            rdflib.term.URIRef('local://Foo/'),
        ),
    }


def test_jsonld_import_without_slashes():
    """
    Import a JSON-LD document with local: IRIs.

    After import, the IRIs are kept as they were.
    """
    source_document = {
        '@context': {
            'title': 'local:title',
        },
        '@id': 'local:boo',
        '@type': 'local:Foo',
        'title': 'Buzinga!',
    }

    graph = rdflib.Graph()
    graph.parse(
        data=json.dumps(source_document),
        format='json-ld',
    )

    assert set(graph) == {
        (
            rdflib.term.URIRef('local:boo'),
            rdflib.term.URIRef('local:title'),
            rdflib.term.Literal('Buzinga!'),
        ),
        (
            rdflib.term.URIRef('local:boo'),
            RDF.type,
            rdflib.term.URIRef('local:Foo'),
        ),
    }
