import json
from itertools import starmap
from typing import Iterator

import frontmatter
import rdflib
from pyld import jsonld

from octiron.plugins.base import Loader
from octiron.types import Triple
from octiron.yaml_extensions import convert_dollar_signs


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

        # meta_data['@context'] = self.context

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

        yield from starmap(Triple, iter(graph))
