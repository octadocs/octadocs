from itertools import starmap
from typing import Iterable, Iterator

import frontmatter
import rdflib

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
            raise ValueError('A-A-A-A!! @context is specified in frontmatter')

        # FIXME get context from somewhere
        meta_data['@context'] = ...

        graph = rdflib.Graph()

        graph.parse(source=str(self.path), format='turtle')
        yield from starmap(Triple, iter(graph))
