from typing import Optional

import rdflib
from mkdocs.structure.pages import Page
from rdflib import URIRef

from octadocs.environment import src_path_to_iri
from octadocs.query import SelectResult, query


def iri_by_page(page: Page) -> URIRef:
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
