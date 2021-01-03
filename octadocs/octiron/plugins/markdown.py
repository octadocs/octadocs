from typing import Iterator

import frontmatter
import rdflib
from rdflib import RDF

from octadocs.octiron.plugins import Loader
from octadocs.octiron.types import OCTA, Triple
from octadocs.octiron.yaml_extensions import as_triple_stream


class MarkdownLoader(Loader):
    """Load semantic data from Markdown front matter."""

    regex = r'\.md$'

    def stream(self) -> Iterator[Triple]:
        """Return stream of triples."""
        meta_data = frontmatter.load(self.path).metadata

        yield from as_triple_stream(
            raw_data=meta_data,
            context=self.context,
            local_iri=self.local_iri,
        )

        # The IRI of the local page is a page.
        # FIXME: maybe this should be in octiron.py and work globally.
        yield Triple(self.local_iri, RDF.type, OCTA.Page)

        # The page will be available on the Web under certain URL.
        if self.global_url is not None:
            yield Triple(
                self.local_iri,
                OCTA.url,
                rdflib.Literal(self.global_url),
            )
