from typing import Optional

import rdflib
from mkdocs.structure.pages import Page

from octadocs.environment import query, src_path_to_iri
from rdflib import URIRef


def iri_by_page(page: Page) -> URIRef:
    """Convert src_path of a file to a Zet IRI."""
    return src_path_to_iri(page.file.src_path)


def get_page_title_by_iri(
    iri: str,
    graph: rdflib.ConjunctiveGraph,
) -> Optional[str]:
    results = query(
        query_text='''
            SELECT ?title WHERE {
                ?page octa:title ?title .
            }
        ''',
        instance=graph,

        page=iri,
    )

    if results:
        return results[0]['title']

    return None
