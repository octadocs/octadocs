import json

from pyld import jsonld
from rdflib import ConjunctiveGraph, URIRef

JSONLD_DOCUMENT = {
    '@context': {
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'label': 'rdfs:label',
        'comment': 'rdfs:comment',
        'rdfs:isDefinedBy': {
            '@type': '@id',
        },
        '@vocab': 'https://example.com/robotics/',
        '@base': 'https://example.com/robotics/',
    },

    '@graph': [
        {
            '@id': 'Robot',
            '@type': 'rdfs:Class',
        },
        {
            '@id': 'Rover',
            'rdfs:subClassOf': {
                '@id': 'Robot',
            },
        },
        {
            '@id': 'opportunity',
            '@type': 'Rover',
            'label': 'Opportunity',
        }
    ],
}


def test_parse_graph():
    serialized_data = json.dumps(JSONLD_DOCUMENT, indent=4)

    graph = ConjunctiveGraph()

    graph.parse(
        data=serialized_data,
        format='json-ld',
        publicID=URIRef('https://example.com/myrobots.jsonld'),
    )

    raise Exception(graph.serialize(format='n3').decode('utf-8'))


def test_expand():
    raise Exception(jsonld.expand(JSONLD_DOCUMENT, options={
        'base': 'https://foo.com',
    }))
