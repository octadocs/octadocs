import dataclasses
from pathlib import Path
from typing import Any

from documented import DocumentedError
from octadocs.query import QueryResult
from typing_extensions import Protocol


class QueryExecutor(Protocol):
    """
    Query executor.

    Allows to abstract away the details of SPARQL query execution from the
    StoredQuery interface.
    """

    def __call__(  # type: ignore
        self,
        query_text: str,
        **kwargs: Any,
    ) -> QueryResult:
        """Run given query with args against an RDF store."""


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
        query_path = self.path.with_name(f'{self.path.name}.sparql')

        try:
            return query_path.read_text()
        except FileNotFoundError as err:
            raise QueryNotFound(path=query_path) from err

    __getitem__ = __getattr__ = _append  # noqa: WPS429
