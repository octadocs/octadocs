from typing import Iterator

import yaml
from octadocs.octiron.plugins import Loader
from octadocs.octiron.yaml_extensions import SafeLoader, as_triple_stream
from octadocs.types import OCTA, Triple
from rdflib import RDF


class YAMLLoader(Loader):
    """Load semantic data from Markdown front matter."""

    regex = r'\.ya*ml$'

    def stream(self) -> Iterator[Triple]:
        """Return stream of triples."""
        if self.path.stem == 'context':
            return

        with open(self.path, 'r') as yaml_file:
            raw_data = yaml.load(yaml_file, Loader=SafeLoader)

        yield from as_triple_stream(
            raw_data=raw_data,
            context=self.context,
            local_iri=self.local_iri,
        )

        # The IRI of the local page is a page.
        # FIXME: maybe this should be in octiron.py and work globally.
        yield Triple(self.local_iri, RDF.type, OCTA.Page)
