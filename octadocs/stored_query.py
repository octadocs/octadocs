import dataclasses
from pathlib import Path
from typing import Callable, Union, Dict

from documented import DocumentedError
from rdflib import Graph
from rdflib.term import Node

QueryResult = Union[
    Dict[str, Node],   # SELECT
    Graph,             # CONSTRUCT
    bool               # ASK
]


QueryExecutor = Callable  # For now


@dataclasses.dataclass
class QueryNotFound(DocumentedError):
    """Stored SPARQL query file {self.path} not found."""

    path: Path


@dataclasses.dataclass(frozen=True)
class StoredQuery:
    """
    Stored SPARQL query access interface.

    Accepts `executor`, which is a function that accepts query text and params,
    returning the query execution result.
    """

    path: Path
    executor: QueryExecutor

    def __call__(self, **kwargs) -> QueryResult:
        """Execute the query."""
        text = self._read_query_text()
        return self.executor(text, **kwargs)

    def _append(self, segment: str) -> 'StoredQuery':
        """Append another segment to the path."""
        return dataclasses.replace(
            self,
            path=self.path / segment,
        )

    def _read_query_text(self) -> str:
        """Fetch query text from disk."""
        query_path = self.path.with_name(self.path.name + '.sparql')

        try:
            return query_path.read_text()
        except FileNotFoundError as err:
            raise QueryNotFound(path=query_path) from err

    __getitem__ = __getattr__ = _append
