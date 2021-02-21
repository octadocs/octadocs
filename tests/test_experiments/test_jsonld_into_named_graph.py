"""
Question about importing JSON-LD @graph contents into a named graph with
specifically provided IRI instead of an IRI taken from the @id.

Published at:

    https://gist.github.com/anatoly-scherbakov/e1c75db34a262f7aa107d82399c50c52

This is supplementary material for this StackOverflow question:

    https://stackoverflow.com/q/65060072/1245471
"""

import json
import operator

from rdflib import ConjunctiveGraph, URIRef, Variable

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
    '@graph': [{
        '@id': 'ex:Robot',
        '@type': 'rdfs:Class',
    }, {
        '@id': 'ex:Rover',
        'rdfs:subClassOf': {
            '@id': 'ex:Robot',
        },
    }]
}


def test_import_jsonld_into_named_graph():
    """Test named graphs we use."""
    graph = ConjunctiveGraph()

    serialized_document = json.dumps(JSONLD_DOCUMENT, indent=4)
    print(serialized_document)

    graph.parse(
        data=serialized_document,
        format='json-ld',
        # All the semantic data about my blog is stored in a particular
        # named graph.
        publicID=PUBLIC_ID,
    )

    assert list(map(
        operator.itemgetter(Variable('g')),
        graph.query(
            'SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o . } } ORDER BY ?g',
        ).bindings,
    )) == [
        URIRef('https://blog.me/JSONLD-and-named-graphs'),
        URIRef('https://myblog.net/rdf/'),
    ]

    # I wanted **one** named graph but got two of them. That's because, when
    # the system was importing contents of @graph block, it was using @id
    # as name for this graph.
    assert graph.query('''
        SELECT * WHERE {
            GRAPH ?g {
                ex:Rover rdfs:subClassOf ex:Robot .
            }
        }
    ''', initNs=NAMESPACES).bindings == [{
        Variable('g'): URIRef('https://blog.me/JSONLD-and-named-graphs'),
    }]

    # `publicID` was used for the part of data which was on the top level
    # of the document.
    assert graph.query('''
        SELECT * WHERE {
            GRAPH ?g {
                blog:JSONLD-and-named-graphs a schema:blogPost .
            }
        }
    ''', initNs=NAMESPACES).bindings == [{
        Variable('g'): PUBLIC_ID,
    }]
