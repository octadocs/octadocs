import logging
import re
import sys
from dataclasses import dataclass, field
from functools import reduce
from pathlib import Path
from types import MappingProxyType
from typing import Dict, Iterable, Iterator, Optional, Type

import owlrl
import rdflib

from octadocs.octiron.context import merge
from octadocs.octiron.context_loaders import (
    context_from_json,
    context_from_yaml,
)
from octadocs.octiron.plugins import (
    Loader,
    MarkdownLoader,
    TurtleLoader,
    YAMLLoader,
)
from octadocs.octiron.types import (
    DEFAULT_CONTEXT,
    DEFAULT_NAMESPACES,
    Context,
    Quad,
    Triple,
)

if sys.version_info >= (3, 8):
    from functools import cached_property  # noqa
else:
    from backports.cached_property import cached_property  # noqa: WPS433,WPS440

logger = logging.getLogger(__name__)

CONTEXT_FORMATS = MappingProxyType({
    'context.json': context_from_json,
    'context.yaml': context_from_yaml,
})


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
    namespaces: Dict[str, rdflib.URIRef] = field(default_factory=dict)

    @cached_property
    def graph(self) -> rdflib.ConjunctiveGraph:
        """Generate and instantiate the RDFLib graph instance."""
        conjunctive_graph = rdflib.ConjunctiveGraph()

        namespaces = dict(DEFAULT_NAMESPACES)
        namespaces.update(self.namespaces)

        for short_name, uri in namespaces.items():
            conjunctive_graph.bind(short_name, uri)

        return conjunctive_graph

    def get_context_per_directory(
        self,
        directory: Path,
    ) -> Context:
        """Find context file per disk directory."""
        return reduce(
            merge,  # type: ignore
            map(
                self._get_context_file,
                reversed(list(self._find_context_files(directory))),
            ),
            dict(DEFAULT_CONTEXT),
        )

    def update_from_file(
        self,
        path: Path,
        local_iri: rdflib.URIRef,
        global_url: Optional[str] = None,
    ) -> None:
        """Update the graph from file determined by given path."""
        context = self.get_context_per_directory(path.parent)
        loader_class = self.get_loader_class_for_path(path)

        if loader_class is None:
            return

        loader_instance = loader_class(
            path=path,
            context=context,
            local_iri=local_iri,
            global_url=global_url,
        )
        triples = loader_instance.stream()

        quads = triples_to_quads(triples=triples, graph=local_iri)

        self.graph.addN(quads)

    def apply_inference(self) -> None:
        """Do whatever is needed after the graph was updated from a file."""
        # FIXME this should be customizable via dependency inversion. Right now
        #   this is hardcoded to run inference rules formulated as SPARQL files.
        logger.info('Inference: OWL RL')
        owlrl.DeductiveClosure(owlrl.OWLRL_Extension).expand(self.graph)

        # Fill in octa:about relationships.
        logger.info(
            'Inference: '
            '?thing octa:subjectOf ?page ⇒ ?page octa:about ?thing .',
        )
        self.graph.update('''
            INSERT {
                ?page octa:about ?thing .
            } WHERE {
                ?thing octa:subjectOf ?page .
            }
        ''')

        logger.info(
            'Inference: ?thing rdfs:label ?label & '
            '?thing octa:page ?page ⇒ ?page octa:title ?label',
        )
        self.graph.update('''
            INSERT {
                ?page octa:title ?title .
            } WHERE {
                ?subject
                    rdfs:label ?title ;
                    octa:subjectOf ?page .
            }
        ''')

        inference_dir = self.root_directory.parent / 'inference'
        if inference_dir.is_dir():
            for sparql_file in inference_dir.iterdir():
                logger.info('Inference: %s', sparql_file.name)
                sparql_text = sparql_file.read_text()
                self.graph.update(sparql_text)

    def get_loader_class_for_path(self, path: Path) -> Optional[Type[Loader]]:
        """Based on file path, determine the loader to use."""
        # TODO dependency inversion
        loaders = [MarkdownLoader, TurtleLoader, YAMLLoader]

        for loader in loaders:
            if re.search(loader.regex, str(path)) is not None:
                return loader

        logger.warning('Cannot find appropriate loader for path: %s', path)
        return None

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

    def _get_context_file(self, path: Path) -> Context:
        """Read and return context file by path."""
        context_loader = CONTEXT_FORMATS[path.name]
        return context_loader(path)
