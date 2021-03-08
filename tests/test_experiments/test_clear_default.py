import rdflib


@pytest.mark.skip('https://github.com/RDFLib/rdflib/issues/1275')
def test_clear_default():
    """Test @base directive with no slash after colon."""
    graph = rdflib.ConjunctiveGraph()

    graph.add((
        rdflib.SDO.title,
        rdflib.RDFS.subPropertyOf,
        rdflib.RDFS.label,
        rdflib.URIRef('https://example.org'),
    ))

    assert list(graph)

    graph.update('CLEAR DEFAULT')

    assert list(graph)
