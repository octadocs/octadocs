"""
Test JSON-LD expand operation in PyLD.

Supplementary code for https://github.com/digitalbazaar/pyld/issues/143

Also published at https://gist.github.com/anatoly-scherbakov/84a539d2f862d1792244168a3b970b57
"""

import json

from pyld import jsonld

JSONLD_DOCUMENT = {
    '@context': {
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'label': 'rdfs:label',
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

EXPANDED_JSONLD_DOCUMENT = [
    {
        '@id': 'https://example.com/robotics/Robot',
        '@type': [
            'http://www.w3.org/2000/01/rdf-schema#Class',
        ],
    },
    {
        '@id': 'https://example.com/robotics/Rover',
        'http://www.w3.org/2000/01/rdf-schema#subClassOf': [
            {'@id': 'https://example.com/robotics/Robot'},
        ],
    },
    {
        '@id': 'https://example.com/robotics/opportunity',
        '@type': ['https://example.com/robotics/Rover'],
        'http://www.w3.org/2000/01/rdf-schema#label': [{
            '@value': 'Opportunity',
        }],
    },
]


SERIALIZED_JSONLD_DOCUMENT = """
{
  "@context": {
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "label": "rdfs:label",
    "@vocab": "https://example.com/robotics/",
    "@base": "https://example.com/robotics/"
  },
  "@graph": [
    {
      "@id": "Robot",
      "@type": "rdfs:Class"
    },
    {
      "@id": "Rover",
      "rdfs:subClassOf": {
        "@id": "Robot"
      }
    },
    {
      "@id": "opportunity",
      "@type": "Rover",
      "label": "Opportunity"
    }
  ]
}
"""


def test_print():
    """Make sure serialization is correct."""
    assert json.dumps(
        JSONLD_DOCUMENT,
        indent=2,
    ) == SERIALIZED_JSONLD_DOCUMENT.strip()


def test_expand_with_with_explicit_base():
    """Expand the document using the explicitly specified base."""
    assert jsonld.expand(
        JSONLD_DOCUMENT,
        options={
            'base': 'https://example.com/robotics/',
        },
    ) == EXPANDED_JSONLD_DOCUMENT


def test_expand_with_base_from_context():
    """Expand the document trying to rely upon @base inside its @context."""

    # This does not work!
    assert jsonld.expand(JSONLD_DOCUMENT) != EXPANDED_JSONLD_DOCUMENT

    # Because the expanded version looks like this:
    assert jsonld.expand(JSONLD_DOCUMENT) == [
        {
            '@id': 'Robot',   # NOT EXPANDED
            '@type': ['http://www.w3.org/2000/01/rdf-schema#Class'],
        },
        {
            '@id': 'Rover',
            'http://www.w3.org/2000/01/rdf-schema#subClassOf': [
                {'@id': 'Robot'},   # NOT EXPANDED
            ],
        },
        {
            '@id': 'opportunity',   # NOT EXPANDED
            '@type': [
                # EXPANDED, but this is because of @vocab not because of @base
                'https://example.com/robotics/Rover',
            ],
            'http://www.w3.org/2000/01/rdf-schema#label': [
                {'@value': 'Opportunity'},
            ],
        },
    ]
