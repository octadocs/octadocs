import re

from mkdocs_meta.settings import LOCAL_IRI_SCHEME
from rdflib import URIRef


def src_path_to_iri(src_path: str) -> URIRef:
    """Convert src_path of a file to a Zet IRI."""
    return URIRef(f'{LOCAL_IRI_SCHEME}{src_path}')


def iri_to_url(iri: str) -> str:
    """Convert Zet IRI into clickable URL."""
    iri = iri.replace(LOCAL_IRI_SCHEME, '')

    if iri.endswith('index.md'):
        return re.sub(
            r'/index\.md$',
            '/',
            iri,
        )

    else:
        return re.sub(
            r'\.md$',
            '',
            iri,
        )
