from octadocs.octiron.yaml_extensions import convert_dollar_signs


def test_value():
    """Values of certain keys should be converted as well as keys."""
    source_document = {
        'rdfs:domain': {
            '$type': '$id',
        },
    }

    expected_document = {
        'rdfs:domain': {
            '@type': '@id',
        },
    }

    assert convert_dollar_signs(source_document) == expected_document
