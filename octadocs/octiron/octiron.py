import logging
import re
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import reduce
from pathlib import Path
from types import MappingProxyType
from typing import Dict, Iterable, Optional, Type

import owlrl
import rdflib
from octadocs.conversions import triples_to_quads
from octadocs.octiron.context import merge
from octadocs.octiron.context_loaders import (
    context_from_json,
    context_from_yaml,
)
from octadocs.octiron.owlrl_named_graph import OWLRLExtensionNamedGraph
from octadocs.octiron.plugins import (
    Loader,
    MarkdownLoader,
    TurtleLoader,
    YAMLLoader,
)
from octadocs.types import DEFAULT_CONTEXT, DEFAULT_NAMESPACES, OCTA, Context
from urlpath import URL

if sys.version_info >= (3, 8):
    from functools import cached_property  # noqa
else:
    from backports.cached_property import cached_property  # noqa: WPS433,WPS440

logger = logging.getLogger(__name__)

CONTEXT_FORMATS = MappingProxyType({
    'context.json': context_from_json,
    'context.yaml': context_from_yaml,
})


class CacheStatus(Enum):
    """Cache condition of a file."""

    NOT_CACHED = auto()
    UP_TO_DATE = auto()
    EXPIRED = auto()


@dataclass
class Octiron:   # noqa: WPS214
    """Convert a lump of goo and data into a semantic graph."""

    root_directory: Path
    custom_namespaces: Dict[str, rdflib.Namespace] = field(default_factory=dict)
    last_modified_timestamp_per_file: Dict[rdflib.URIRef, float] = field(
        default_factory=dict,
        metadata={
            '__doc__': 'Time when every file was last imported into the graph.',
        },
    )

    @cached_property
    def namespaces(self):
        """
        Join the provided custom namespaces with the defaults.

        Returns all namespaces registered with this Octiron instance.
        """
        namespaces = dict(DEFAULT_NAMESPACES)
        namespaces.update(self.custom_namespaces)

        return namespaces

    @cached_property
    def graph(self) -> rdflib.ConjunctiveGraph:
        """Generate and instantiate the RDFLib graph instance."""
        conjunctive_graph = rdflib.ConjunctiveGraph()

        for short_name, namespace in self.namespaces.items():
            conjunctive_graph.bind(short_name, namespace)

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

    def create_file_cache_status(
        self,
        local_iri: rdflib.URIRef,
        last_modification_timestamp_on_disk: float,
    ) -> CacheStatus:
        """Determine caching status of a file."""
        cached_modification_time = self.last_modified_timestamp_per_file.get(
            local_iri,
        )

        if cached_modification_time is None:
            return CacheStatus.NOT_CACHED

        elif cached_modification_time < last_modification_timestamp_on_disk:
            return CacheStatus.EXPIRED

        return CacheStatus.UP_TO_DATE

    def clear_named_graph(self, local_iri: rdflib.URIRef) -> None:
        """Remove all triples in the specified named graph."""
        # Ugly formatting is used because of:
        #   https://github.com/RDFLib/rdflib/issues/1277
        self.graph.update(f'CLEAR GRAPH <{local_iri}>')

    def update_from_file(  # noqa: WPS210
        self,
        path: Path,
        local_iri: rdflib.URIRef,
        global_url: Optional[str] = None,
    ) -> None:
        """Update the graph from file determined by given path."""
        # Create a shorter (printable) version of the path for logging messages.
        try:
            relative_path = path.relative_to(self.root_directory)
        except ValueError:
            relative_path = path

        file_last_modification_time = path.stat().st_mtime

        cache_status = self.create_file_cache_status(
            local_iri=local_iri,
            last_modification_timestamp_on_disk=file_last_modification_time,
        )

        if cache_status == CacheStatus.UP_TO_DATE:
            logger.info('Skipping %s (cached and up to date)', relative_path)
            return

        elif cache_status == CacheStatus.EXPIRED:
            self.clear_named_graph(local_iri)

        context = self.get_context_per_directory(path.parent)
        loader_class = self.get_loader_class_for_path(path)

        if loader_class is None:
            return

        logger.info(
            'Importing %s via %s (%s)',
            relative_path,
            loader_class.__name__,
            'not cached before' if (
                cache_status == CacheStatus.NOT_CACHED
            ) else 'cached but expired',
        )

        loader_instance = loader_class(
            path=path,
            context=context,
            local_iri=local_iri,
            global_url=global_url,
        )
        triples = loader_instance.stream()

        quads = triples_to_quads(triples=triples, graph=local_iri)

        self.graph.addN(quads)

        self.add_metadata(
            local_iri=local_iri,
        )

        # Store the file last modification time
        self.last_modified_timestamp_per_file[local_iri] = (
            file_last_modification_time
        )

    def add_metadata(self, local_iri: rdflib.URIRef) -> None:
        """Store metadata about a source file."""
        local_url = URL(local_iri.toPython())
        parent_iri = rdflib.URIRef(str(local_url.parent))
        file_name = rdflib.Literal(local_url.name)
        directory_name = rdflib.Literal(local_url.parent.name)

        quads = [
            (
                local_iri,
                rdflib.RDF.type,
                OCTA.Directory,
                local_iri,
            ),
            (
                parent_iri,
                OCTA.isParentOf,
                local_iri,
                local_iri,
            ),
            (
                parent_iri,
                OCTA.fileName,
                directory_name,
                local_iri,
            ),
            (
                local_iri,
                OCTA.fileName,
                file_name,
                local_iri,
            ),
        ]

        self.graph.addN(quads)

    def apply_inference(self) -> None:  # noqa: WPS213
        """Do whatever is needed after the graph was updated from a file."""
        logger.info('Inference: OWL RL started...')
        owlrl.DeductiveClosure(OWLRLExtensionNamedGraph).expand(self.graph)
        logger.info('Inference: OWL RL complete.')

        # Custom inference queries
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
