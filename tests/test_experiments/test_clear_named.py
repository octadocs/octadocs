import pytest
import rdflib


@pytest.mark.skip('https://github.com/RDFLib/rdflib/issues/1277')
def test_clear_named():
    """Test @base directive with no slash after colon."""
    graph = rdflib.ConjunctiveGraph()

    graph.add((
        rdflib.SDO.title,
        rdflib.RDFS.subPropertyOf,
        rdflib.RDFS.label,
        rdflib.URIRef('https://example.org'),
    ))

    assert list(graph)

    # Fails:
    #     E   pyparsing.ParseException: Expected end of text, found 'C'
    #         (at char 0), (line:1, col:1)
    graph.update('CLEAR GRAPH ?g', initBindings={
        'g': rdflib.URIRef('https://example.org'),
    })

    assert not list(graph)
