"""
Import JSON-LD document into RDFLib graph.

The schema of @base IRI can lead RDFLib to silently refuse the import.

This is supplementary code for: https://github.com/RDFLib/rdflib-jsonld/issues/97
"""

import json
import textwrap

import pytest
from rdflib import ConjunctiveGraph


def get_json_ld_document(base: str):
    return {
        '@context': {
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            '@base': base,
        },

        '@graph': [
            {
                '@id': 'Robot',
                '@type': 'rdfs:Class',
            },
            {
                '@id': 'wall-e',
                '@type': 'Robot',
                'rdfs:label': 'Wall-E',
            }
        ],
    }


def get_n3_form(base: str) -> str:
    return textwrap.dedent(f'''
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        <{base}Robot> a rdfs:Class .

        <{base}wall-e> a <{base}Robot> ;
            rdfs:label "Wall-E" .
    ''').strip()


@pytest.mark.skip('Illustrates a bug')
@pytest.mark.parametrize(
    'base',
    [
        # Good base IRIs. TEST PASSES ON THESE.
        'http://robotics.example.com/robots/',
        'https://robotics.example.com/robots/',
        'ftp://robotics.example.com/robots/',
        'file://robotics.example.com/robots/',

        # Bad base IRIs. TEST FAILS ON THESE.
        'ipns://robotics.example.com/robots/',
        'tftp://robotics.example.com/robots/',
        'ntp://robotics.example.com/robots/',
        'local://robotics.example.com/robots/',
    ]
)
def test_parse_jsonld_document_with_different_base_urls(base: str):
    serialized_data = json.dumps(get_json_ld_document(
        base=base,
    ), indent=4)

    graph = ConjunctiveGraph()

    graph.parse(
        data=serialized_data,
        format='json-ld',
    )

    assert list(graph), 'Graph is empty because the base IRI is bad.'

    actual_n3_form = graph.serialize(
        format='n3',
    ).decode('utf-8').strip()
    expected_n3_form = get_n3_form(base=base)

    assert actual_n3_form == expected_n3_form
