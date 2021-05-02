from typing import Iterator, Optional

import rdflib
from mkdocs.structure.pages import Page
from octadocs.query import SelectResult, query
from octadocs.types import LOCAL, Quad, Triple


def iri_by_page(page: Page) -> rdflib.URIRef:
    """Convert src_path of a file to a Zet IRI."""
    return src_path_to_iri(page.file.src_path)


def get_page_title_by_iri(
    iri: str,
    graph: rdflib.ConjunctiveGraph,
) -> Optional[str]:
    rows: SelectResult = query(  # type: ignore
        query_text='''
            SELECT ?title WHERE {
                ?page octa:title ?title .
            }
        ''',
        instance=graph,

        page=iri,
    )

    if rows:
        return rows[0]['title']

    return None


def triples_to_quads(
    triples: Iterator[Triple],
    graph: rdflib.URIRef,
) -> Iterator[Quad]:
    """Convert sequence of triples to sequence of quads."""
    yield from (
        triple.as_quad(graph)
        for triple in triples
    )


def src_path_to_iri(src_path: str) -> rdflib.URIRef:
    """Convert src_path of a file to a Zet IRI."""
    return rdflib.URIRef(f'{LOCAL}{src_path}')
