import json
import re
from dataclasses import dataclass, field
from functools import partial, reduce
from pathlib import Path
from typing import Iterable, Dict, Any, Optional, Type, Iterator

import rdflib
import yaml
from deepmerge import always_merger

from octiron.plugins.base import Loader
from octiron.plugins.markdown import MarkdownLoader
from octiron.plugins.turtle import TurtleLoader
from octiron.types import Context, Triple, Quad

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
        '@type': '@id',
    },
    'rdfs:subClassOf': {
        '@type': '@id',
    },
}


def triples_to_quads(
    triples: Iterator[Triple],
    graph: rdflib.URIRef,
) -> Iterator[Quad]:
    """Convert sequence of triples to sequence of quads."""
    yield from (
        triple.as_quad(graph)
        for triple in triples
    )


@dataclass
class Octiron:
    """Convert a lump of goo and data into a semantic graph."""

    root_directory: Path
    graph: rdflib.ConjunctiveGraph = field(
        default_factory=rdflib.ConjunctiveGraph,
    )

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

    def _get_context_file(self, path: Path) -> Dict[str, Any]:
        """Read and return context file by path."""
        loader = CONTEXT_FORMATS[path.name]

        with path.open('r') as context_data_stream:
            yield loader(context_data_stream)

    def get_context_per_directory(
        self,
        directory: Path,
    ) -> Context:
        """Find context file per disk directory."""
        return reduce(
            always_merger.merge,
            map(
                self._get_context_file,
                reversed(list(self._find_context_files(directory))),
            ),
            DEFAULT_CONTEXT,
        )

    def update_from_file(self, path: Path, iri: rdflib.URIRef) -> None:
        """Update the graph from file determined by given path."""
        context = self.get_context_per_directory(path.parent)
        loader_class = self.get_loader_class_for_path(path)
        loader_instance = loader_class(
            path=path,
            context=context,
        )
        triples = loader_instance.stream()

        quads = triples_to_quads(triples=triples, graph=iri)

        self.graph.addN(quads)

    def get_loader_class_for_path(self, path: Path) -> Type[Loader]:
        """Based on file path, determine the loader to use."""
        # TODO dependency inversion
        for loader in [
            MarkdownLoader,
            TurtleLoader,
        ]:
            if re.search(loader.regex, str(path)) is not None:
                return loader

        raise ValueError(f'Cannot find appropriate loader for path: {path}')
