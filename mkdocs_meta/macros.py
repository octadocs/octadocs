import cgi
import io
from base64 import b64encode
from unittest.mock import patch

import pydotplus
import rdflib
from macros.plugin import MacrosPlugin
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


def sparql(instance: rdflib.ConjunctiveGraph, query: str) -> rdflib.Graph:
    result: SPARQLResult = instance.query(query)
    return result.graph


def define_env(env: MacrosPlugin) -> MacrosPlugin:

    env.filter(graph)
    env.filter(sparql)

    return env
