import re
from typing import Dict, List

import rdflib
from rdflib import URIRef, term
from rdflib.plugins.sparql.processor import SPARQLResult

from octadocs.octiron.types import LOCAL


def query(
    query_text: str,
    instance: rdflib.ConjunctiveGraph,
    **kwargs: str,
):
    """Run SPARQL SELECT query and return formatted result."""
    sparql_result: SPARQLResult = instance.query(
        query_text,
        initBindings=kwargs,
    )

    if sparql_result.askAnswer is not None:
        return sparql_result.askAnswer

    return _format_query_bindings(sparql_result.bindings)


def iri_to_url(iri: str) -> str:
    """Convert Zet IRI into clickable URL."""
    iri = iri.replace(str(LOCAL), '')

    if iri.endswith('index.md'):
        return re.sub(
            r'/index\.md$',
            '/',
            iri,
        )

    else:
        return re.sub(
            r'\.md$',
            '',
            iri,
        )


def src_path_to_iri(src_path: str) -> URIRef:
    """Convert src_path of a file to a Zet IRI."""
    return URIRef(f'{LOCAL}{src_path}')


def _format_query_bindings(
    bindings: List[Dict[rdflib.Variable, term.Identifier]],
) -> List[Dict[str, term.Identifier]]:
    """
    Format bindings before returning them.

    Converts Variable to str for ease of addressing.
    """
    return [
        {
            str(variable_name): rdf_value
            for variable_name, rdf_value
            in row.items()
        }
        for row in bindings
    ]
