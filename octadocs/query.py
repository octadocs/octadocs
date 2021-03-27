from typing import Dict, List, Optional, Union

import rdflib
from rdflib import Graph, term
from rdflib.plugins.sparql.processor import SPARQLResult
from typing_extensions import Protocol

SelectRow = Dict[str, term.Node]


class SelectResult(List[SelectRow]):
    """SPARQL SELECT query result."""

    @property
    def first(self) -> Optional[SelectRow]:
        """Return first element of the list."""
        return self[0] if self else None


QueryResult = Union[
    SelectResult,   # SELECT
    Graph,          # CONSTRUCT
    bool,           # ASK
]


class Query(Protocol):
    """Query protocol."""

    def __call__(
        self,
        query_text: str,
        instance: rdflib.ConjunctiveGraph,
        **kwargs: str,
    ) -> QueryResult:
        """Query prototype."""


def query(
    query_text: str,
    instance: rdflib.ConjunctiveGraph,
    **kwargs: str,
) -> QueryResult:
    """Run SPARQL SELECT query and return formatted result."""
    sparql_result: SPARQLResult = instance.query(
        query_text,
        initBindings=kwargs,
    )

    if sparql_result.askAnswer is not None:
        return sparql_result.askAnswer

    if sparql_result.graph is not None:
        graph: rdflib.Graph = sparql_result.graph
        for prefix, namespace in instance.namespaces():
            graph.bind(prefix, namespace)

        return graph

    return _format_query_bindings(sparql_result.bindings)


def _format_query_bindings(
    bindings: List[Dict[rdflib.Variable, term.Identifier]],
) -> SelectResult:
    """
    Format bindings before returning them.

    Converts Variable to str for ease of addressing.
    """
    return SelectResult(
        {
            str(variable_name): rdf_value
            for variable_name, rdf_value
            in row.items()
        }
        for row in bindings
    )
