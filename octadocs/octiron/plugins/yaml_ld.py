from typing import Iterator

import yaml
from rdflib import RDF

from octadocs.octiron.plugins import Loader
from octadocs.octiron.types import OCTA, Triple
from octadocs.octiron.yaml_extensions import (
    as_triple_stream,
)

try:
    from yaml import CSafeDumper as SafeDumper
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeDumper
    from yaml import SafeLoader


class YAMLLoader(Loader):
    """Load semantic data from Markdown front matter."""

    regex = r'\.ya*ml$'

    def stream(self) -> Iterator[Triple]:
        """Return stream of triples."""
        with open(self.path, 'r') as yaml_file:
            raw_data = yaml.load(yaml_file)

        yield from as_triple_stream(
            raw_data=raw_data,
            context=self.context,
            local_iri=self.local_iri,
        )

        # The IRI of the local page is a page.
        # FIXME: maybe this should be in octiron.py and work globally.
        yield Triple(self.local_iri, RDF.type, OCTA.Page)
