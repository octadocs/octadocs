import json
from itertools import starmap
from typing import Iterator

import frontmatter
import rdflib
from pyld import jsonld
from rdflib import RDF

from octadocs.octiron.plugins import Loader
from octadocs.octiron.types import Triple, OCTA
from octadocs.octiron.yaml_extensions import convert_dollar_signs


class MarkdownLoader(Loader):
    """Load semantic data from Markdown front matter."""

    regex = r'\.md$'

    def stream(self) -> Iterator[Triple]:
        """Return stream of triples."""
        meta_data = frontmatter.load(self.path).metadata

        if not meta_data:
            return

        meta_data = convert_dollar_signs(meta_data)

        if meta_data.get('@context'):
            raise ValueError('A-A-A!!! @context is specified in front matter!')

        if '@id' in meta_data:
            # The author specified an IRI the document tells us about. Let us
            # link this IRI to the local document IRI.
            meta_data['octa:subjectOf'] = self.local_iri

        else:
            # The document author did not tell us about what their document is.
            # In this case, we assume that the local_iri of the document file
            # is the subject of the document description.
            meta_data['@id'] = self.local_iri

        # Reason: https://github.com/RDFLib/rdflib-jsonld/issues/97
        # If we don't expand with an explicit @base, import will fail silently.
        meta_data = jsonld.expand(
            meta_data,
            options={
                'base': 'local:',
                'expandContext': self.context,
            },
        )

        # Reason: https://github.com/RDFLib/rdflib-jsonld/issues/98
        # If we don't flatten, @included sections will not be imported.
        meta_data = jsonld.flatten(meta_data)

        serialized_meta_data = json.dumps(meta_data, indent=4)

        graph = rdflib.Graph()

        graph.parse(
            data=serialized_meta_data,
            format='json-ld',
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

        yield from starmap(Triple, iter(graph))
