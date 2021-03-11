import json

from rdflib import Graph, Literal, URIRef


def test_parse_compacted_uri():
    rdfs = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

    json_document = {
        '@context': {
            'rdfs': rdfs,
        },
        '@id': 'rdfs:',
        'rdfs:label': 'boo!',
    }

    g = Graph()

    g.parse(
        data=json.dumps(json_document),
        format='json-ld',
    )

    triple, = list(g)

    assert triple == (
        URIRef(rdfs),
        URIRef(f'{rdfs}label'),
        Literal('boo!')
    )
