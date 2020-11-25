import cgi
import io
import textwrap
from base64 import b64encode
from functools import partial, wraps
from typing import Any, Dict, List, TypedDict, Union, Optional
from unittest.mock import patch

import pydotplus
import rdflib
from macros.plugin import MacrosPlugin
from rdflib import Variable
from rdflib.plugins.sparql.processor import SPARQLResult
from rdflib.tools.rdf2dot import rdf2dot

import html


def graph(instance: rdflib.ConjunctiveGraph) -> str:
    """
    Render RDF graph visually as PNG image.

    Idea: https://stackoverflow.com/a/61483971/1245471
    """
    dot_description = io.StringIO()

    with patch('rdflib.tools.rdf2dot.cgi', html):
        # FIXME hack, fixes this: https://github.com/RDFLib/rdflib/issues/1110
        rdf2dot(instance, dot_description)

    dg = pydotplus.graph_from_dot_data(dot_description.getvalue())
    png = dg.create_png()

    encoded_png = b64encode(png).decode('utf-8')

    return f'<img src="data:image/png;base64,{encoded_png}" />'


def n3(instance: rdflib.ConjunctiveGraph) -> str:
    """Serialize graph as n3."""
    serialized_document = instance.serialize(format='n3').decode('utf-8')
    return (
        '```n3\n'
        f'{serialized_document}\n'
        '```\n'
    )


def sparql(
    instance: rdflib.ConjunctiveGraph,
    query: str,
    **kwargs: str,
) -> SPARQLResult:
    bindings = {
        argument_name: argument_value
        for argument_name, argument_value in kwargs.items()
    }

    return instance.query(query, initBindings=bindings)


def _render_as_row(row: Dict[Variable, Any]) -> str:
    result = ' | '.join(row.values())
    return f'| {result} |'


def table(result: SPARQLResult) -> str:
    headers = ' | '.join(str(v) for v in result.vars)

    rows = '\n'.join(
        _render_as_row(row)
        for row in result.bindings
    )

    separators = '| ' + (' --- |' * len(result.vars))

    return f'''
---
| {headers} |
{separators}
{rows}
'''


class Card(TypedDict):
    url: str
    label: str
    comment: str


def gallery(query_result: SPARQLResult) -> List[Card]:
    return [{
        str(variable): str(rdf_value) if isinstance(rdf_value, rdflib.URIRef) else rdf_value.value
        for variable, rdf_value
        in row.items()
    } for row in query_result.bindings]


def get_bindings(
    kwargs: Dict[str, Optional[Union[rdflib.URIRef, str, int, float]]],
) -> Dict[str, Union[rdflib.URIRef, rdflib.Literal]]:
    return {
        argument_name: argument_value if (
            isinstance(argument_value, rdflib.URIRef)
        ) else rdflib.Literal(argument_value)
        for argument_name, argument_value in kwargs.items()
    }


class SelectResult(list):
    columns: List[str]

    def __init__(self, columns: List[str], items: List[dict]):
        self.extend(items)
        self.columns = columns


def select(
    query: str,
    instance: rdflib.ConjunctiveGraph,
    **kwargs: str,
):
    """Run SPARQL SELECT query and return formatted result."""
    sparql_result: SPARQLResult = instance.query(
        query,
        initBindings=get_bindings(kwargs),
    )

    return [{
        str(variable): str(rdf_value) if (
            isinstance(rdf_value, rdflib.URIRef)
        ) else rdf_value.value
        for variable, rdf_value
        in row.items()
    } for row in sparql_result.bindings]


def define_env(env: MacrosPlugin) -> MacrosPlugin:
    env.filter(graph)
    env.filter(sparql)
    env.filter(n3)
    env.filter(table)
    env.filter(gallery)

    env.macro(partial(
        select,
        instance=env.variables.graph,
    ), name='select')

    # FIXME this is hardcode, needs to be defined dynamically
    env.variables['rdfs'] = rdflib.Namespace(
        'http://www.w3.org/2000/01/rdf-schema#',
    )

    return env
