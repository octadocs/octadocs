import cgi
import io
import textwrap
from base64 import b64encode
from typing import Any, Dict
from unittest.mock import patch

import pydotplus
import rdflib
from macros.plugin import MacrosPlugin
from rdflib import Variable
from rdflib.plugins.sparql.processor import SPARQLResult
from rdflib.tools.rdf2dot import rdf2dot

import html


def graph(instance: rdflib.ConjunctiveGraph) -> str:
    dot_description = io.StringIO()

    with patch('rdflib.tools.rdf2dot.cgi', html):
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


def sparql(instance: rdflib.ConjunctiveGraph, query: str) -> SPARQLResult:
    return instance.query(query)


def _render_as_row(row: Dict[Variable, Any]) -> str:
    result = ' | '.join(row.values())
    return f'| {result} |'


def table(result: SPARQLResult) -> str:
    headers = ' | '.join(str(v) for v in result.vars)

    rows = '\n'.join(
        _render_as_row(row)
        for row in result.bindings
    )

    return f'''
---
| {headers} |
| --- | --- | --- | --- |
{rows}
'''


def define_env(env: MacrosPlugin) -> MacrosPlugin:
    env.filter(graph)
    env.filter(sparql)
    env.filter(n3)
    env.filter(table)

    return env
