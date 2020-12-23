"""
Question about importing JSON-LD @included contents.

Published at:

    https://gist.github.com/anatoly-scherbakov/d5ddeb6a0a8651ba5d148aa36a752699

This is supplementary material for this GitHub issue:

    https://github.com/RDFLib/rdflib-jsonld/issues/98
"""

import json
import operator

import pytest
from pyld import jsonld
from rdflib import ConjunctiveGraph, Variable, URIRef


NAMESPACES = {
    'schema': 'https://schema.org/',
    'blog': 'https://blog.me/',
    'ex': 'https://example.org/',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
}


PUBLIC_ID = URIRef('https://myblog.net/rdf/')


JSONLD_DOCUMENT = {
    '@context': NAMESPACES,

    # This document describes an article in my blog. This article has a few
    # properties.
    '@id': 'blog:JSONLD-and-named-graphs',
    '@type': 'schema:blogPost',
    'rdfs:label': 'JSON-LD and Named Graphs',

    # The article I am going to write requires some example RDF data, which I
    # am trying to describe using @graph keyword. These are not directly linked
    # to the article.
    '@included': [{
        '@id': 'ex:Robot',
        '@type': 'rdfs:Class',
    }, {
        '@id': 'ex:Rover',
        'rdfs:subClassOf': {
            '@id': 'ex:Robot',
        },
    }]
}


@pytest.mark.skip('Illustrates a bug')
@pytest.mark.parametrize('flatten_before_import', [False, True])
def test_import_jsonld_into_named_graph(flatten_before_import: bool):
    """Test named graphs we use."""
    graph = ConjunctiveGraph()

    jsonld_document = JSONLD_DOCUMENT

    if flatten_before_import:
        jsonld_document = jsonld.flatten(jsonld_document)

    serialized_document = json.dumps(jsonld_document, indent=4)
    print(serialized_document)

    graph.parse(
        data=serialized_document,
        format='json-ld',
        publicID=PUBLIC_ID,
    )

    print(graph.serialize(format='n3').decode('utf-8'))

    # Make sure only one NAMED GRAPH is created on import.
    assert list(map(
        operator.itemgetter(Variable('g')),
        graph.query(
            'SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o . } } ORDER BY ?g',
        ).bindings,
    )) == [
        URIRef('https://myblog.net/rdf/'),
    ]

    # The information in @included section was properly parsed.
    assert graph.query('''
        SELECT * WHERE {
            GRAPH ?g {
                ex:Rover rdfs:subClassOf ex:Robot .
            }
        }
    ''', initNs=NAMESPACES).bindings == [{
        Variable('g'): PUBLIC_ID,
    }]

    # The information in the root was properly parsed.
    assert graph.query('''
        SELECT * WHERE {
            GRAPH ?g {
                blog:JSONLD-and-named-graphs a schema:blogPost .
            }
        }
    ''', initNs=NAMESPACES).bindings == [{
        Variable('g'): PUBLIC_ID,
    }]
