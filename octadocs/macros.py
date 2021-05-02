import html
import io
from base64 import b64encode
from functools import partial
from typing import Any, Dict, Optional
from unittest.mock import patch

import pydotplus
import rdflib
from mkdocs_macros.plugin import MacrosPlugin
from octadocs.conversions import iri_by_page, src_path_to_iri
from octadocs.environment import iri_to_url
from octadocs.query import query
from rdflib.plugins.sparql.processor import SPARQLResult
from rdflib.tools.rdf2dot import rdf2dot


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


def turtle(instance: rdflib.ConjunctiveGraph) -> str:
    """Serialize graph as n3."""
    serialized_document = instance.serialize(format='turtle').decode('utf-8')
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


def _render_as_row(row: Dict[rdflib.Variable, Any]) -> str:  # type: ignore
    """Render row of a Markdown table."""
    formatted_row = ' | '.join(row.values())
    return f'| {formatted_row} |'


def table(query_result: SPARQLResult) -> str:
    """Render as a Markdown table."""
    headers = ' | '.join(str(cell) for cell in query_result.vars)

    rows = '\n'.join(
        _render_as_row(row)
        for row in query_result.bindings
    )

    separators = '| ' + (' --- |' * len(query_result.vars))  # noqa: WPS336

    return f'''
---
| {headers} |
{separators}
{rows}
'''


def construct(
    query_text: str,
    instance: rdflib.ConjunctiveGraph,
    **kwargs: str,
) -> rdflib.Graph:
    """Run SPARQL SELECT query and return formatted result."""
    sparql_result: SPARQLResult = instance.query(
        query_text,
        initBindings=kwargs,
    )

    return sparql_result.graph


def url(
    resource: rdflib.URIRef,
    graph: rdflib.ConjunctiveGraph
) -> Optional[str]:
    """Convert a URIRef to a clickable URL."""
    bindings = graph.query(
        'SELECT ?url WHERE { ?resource octa:subjectOf/octa:url ?url . } ',
        initBindings={
            'resource': resource,
        }
    ).bindings

    if not bindings:
        return None

    return '/' + bindings[0][rdflib.Variable('url')].value


def label(
    resource: rdflib.URIRef,
    graph: rdflib.ConjunctiveGraph
) -> Optional[str]:
    """Convert a URIRef to a clickable URL."""
    bindings = graph.query(
        'SELECT ?label WHERE { ?resource rdfs:label ?label . } ',
        initBindings={
            'resource': resource,
        }
    ).bindings

    if not bindings:
        return None

    return bindings[0][rdflib.Variable('label')].value


def define_env(env: MacrosPlugin) -> MacrosPlugin:  # noqa: WPS213
    """Create mkdocs-macros Jinja environment."""
    env.filter(graph)
    env.filter(sparql)
    env.filter(turtle)
    env.filter(table)

    octiron = env.variables.octiron

    env.macro(
        partial(
            query,
            instance=env.variables.graph,
        ),
        name='query',
    )

    env.macro(
        partial(
            construct,
            instance=env.variables.graph,
        ),
        name='construct',
    )

    env.macro(
        partial(
            url,
            graph=env.variables.graph,
        ),
        name='url',
    )

    env.filter(
        partial(
            url,
            graph=env.variables.graph,
        ), name='url',
    )

    env.filter(
        partial(
            label,
            graph=env.variables.graph,
        ),
        name='label',
    )

    env.macro(iri_to_url)
    env.macro(src_path_to_iri)

    env.filter(iri_to_url)

    env.filter(iri_by_page)
    env.macro(iri_by_page)

    # Update context with namespaces
    env.variables.update(octiron.namespaces)

    env.variables['URIRef'] = rdflib.URIRef

    return env
