import json
from dataclasses import dataclass
from functools import lru_cache, partial, reduce
from pathlib import Path
from typing import Iterable, Dict, Any, Optional

import rdflib
import yaml
from deepmerge import always_merger
from yaml import Loader

CONTEXT_FORMATS = {
    'context.json': json.load,

    # FIXME we need $ conversion for YAML files.
    'context.yaml': partial(
        yaml.load,
        Loader=Loader,
    ),
}

DEFAULT_CONTEXT = {
    '@vocab': 'local:',
    '@base': 'local:',

    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'schema': 'https://schema.org/',
    'octa': 'https://ns.octadocs.io/',

    'label': 'rdfs:label',
    'comment': 'rdfs:comment',
    'rdfs:isDefinedBy': {
        '$type': '@id',
    },
    'rdfs:subClassOf': {
        '$type': '@id',
    },
}


@dataclass
class Octiron:
    """Convert a lump of goo and data into a semantic graph."""

    root_directory: Path
    graph: Optional[rdflib.ConjunctiveGraph] = None

    def _find_context_files(self, directory: Path) -> Iterable[Path]:
        """
        Find all context files relevant to particular directory.

        Files are ordered from the deepest to the upmost.
        """
        for context_directory in (directory, *directory.parents):
            for filename in CONTEXT_FORMATS.keys():
                context_path = context_directory / filename

                if context_path.is_file():
                    yield context_path

            if context_directory == self.root_directory:
                return

    @lru_cache
    def _get_context_file(self, path: Path) -> Dict[str, Any]:
        """Read and return context file by path."""
        loader = CONTEXT_FORMATS[path.name]

        with path.open('r') as context_data_stream:
            yield loader(context_data_stream)

    @lru_cache
    def get_context_per_directory(
        self,
        directory: Path,
    ) -> Dict[str, Any]:
        """Find context file per disk directory."""
        return reduce(
            always_merger.merge,
            map(
                self._get_context_file,
                reversed(list(self._find_context_files(directory))),
            ),
            DEFAULT_CONTEXT,
        )

    def update_from_file(self, path: Path) -> None:
        """Update the graph from file determined by given path."""
        # FIXME how to register and call plugins? Every plugin should yield
        #   a stream of triples. That will ensure independence of rdflib.
        #   I think a regex for file path will be a good idea.
        context = self.get_context_per_directory(path.parent)
