import re
from typing import Dict, Optional, Union

import rdflib
from rdflib import URIRef
from rdflib.plugins.sparql.processor import SPARQLResult

from octadocs.settings import LOCAL_IRI_SCHEME


def query(
    query_text: str,
    instance: rdflib.ConjunctiveGraph,
    **kwargs: str,
):
    """Run SPARQL SELECT query and return formatted result."""
    sparql_result: SPARQLResult = instance.query(
        query_text,
        initBindings=get_bindings(kwargs),
    )

    if sparql_result.askAnswer is not None:
        return sparql_result.askAnswer

    return _format_query_bindings(sparql_result.bindings)


def iri_to_url(iri: str) -> str:
    """Convert Zet IRI into clickable URL."""
    iri = iri.replace(LOCAL_IRI_SCHEME, '')

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
    return URIRef(f'{LOCAL_IRI_SCHEME}{src_path}')


def get_bindings(
    kwargs: Dict[str, Optional[Union[rdflib.URIRef, str, int, float]]],
) -> Dict[str, Union[rdflib.URIRef, rdflib.Literal]]:
    return {
        argument_name: argument_value if True or (
            isinstance(argument_value, rdflib.URIRef)
        ) else rdflib.Literal(argument_value)
        for argument_name, argument_value in kwargs.items()
    }


def _format_sparql_variable_value(rdf_value):
    if isinstance(rdf_value, rdflib.URIRef):
        return str(rdf_value)

    elif isinstance(rdf_value, rdflib.BNode):
        return str(rdf_value)

    return rdf_value.value


def _format_query_bindings(bindings):
    return [{
        str(variable): _format_sparql_variable_value(rdf_value)
        for variable, rdf_value
        in row.items()
    } for row in bindings]
