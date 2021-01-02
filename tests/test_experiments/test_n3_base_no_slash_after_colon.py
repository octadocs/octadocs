"""
Test for GitHub issue: https://github.com/RDFLib/rdflib/issues/1216
"""
import pytest
import rdflib

from octadocs.octiron.types import LOCAL

DOCUMENT = f"""
@base <{LOCAL}> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<class_to_class>
  a
    rdfs:Class ,
    <Category> ;

  <color> "blue" ;
  <priority> 4 .
"""


@pytest.mark.skip('https://github.com/RDFLib/rdflib/issues/1216')
def test_no_slash_after_colon():
    """Test @base directive with no slash after colon."""
    graph = rdflib.ConjunctiveGraph()
    graph.parse(
        data=DOCUMENT,
        format='n3',
    )

    # Raises ValueError:
    #   Base <LOCAL> has no slash after colon - with relative 'class_to_class'.
