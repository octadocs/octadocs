import logging
import operator
from functools import partial
from pathlib import Path
from typing import Callable, Dict, Optional, Union

import owlrl
import rdflib
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Navigation, Section
from mkdocs.structure.pages import Page
from typing_extensions import TypedDict

from octadocs import settings
from octadocs.environment import query, src_path_to_iri
from octadocs.navigation import OctadocsNavigationProcessor
from octiron import Octiron
from octiron.types import OCTA, LOCAL

NavigationItem = Union[Page, Section]

logger = logging.getLogger(__name__)


class ConfigExtra(TypedDict):
    """Extra portion of the config which we put our graph into."""

    graph: rdflib.ConjunctiveGraph


class Config(TypedDict):
    """MkDocs configuration."""

    docs_dir: str
    extra: Optional[ConfigExtra]


class TemplateContext(TypedDict):
    """Context for the native MkDocs page rendering engine."""

    graph: rdflib.ConjunctiveGraph
    iri: rdflib.URIRef
    this: rdflib.URIRef
    query: Callable[[str], Dict[str, rdflib.term.Identifier]]

    # FIXME this is hardcode and should be removed
    rdfs: rdflib.Namespace


def update_graph_from_n3_file(
    mkdocs_file: File,
    docs_dir: Path,
    universe: rdflib.ConjunctiveGraph,
):
    """Load data from Turtle file into the graph."""
    universe.parse(
        source=str(docs_dir / mkdocs_file.src_path),
        format='n3',
        publicID=src_path_to_iri(mkdocs_file.src_path),
    )

    return universe


def get_template_by_page(
    page: Page,
    graph: rdflib.ConjunctiveGraph,
) -> Optional[str]:
    iri = rdflib.URIRef(f'{settings.LOCAL_IRI_SCHEME}{page.file.src_path}')

    bindings = graph.query(
        'SELECT ?template_name WHERE { ?iri octa:template ?template_name }',
        initBindings={
            'iri': iri,
        },
    ).bindings

    if bindings:
        return bindings[0]['template_name'].value

    return None


class OctaDocsPlugin(BasePlugin):
    """MkDocs Meta plugin."""

    octiron: Octiron

    def on_config(self, config: Config) -> Config:
        self.octiron = Octiron(
            root_directory=Path(config['docs_dir']),
            namespaces={
                'octa': OCTA,
                'local': LOCAL,
            }
        )

        if config['extra'] is None:
            config['extra'] = {}

        config['extra']['graph'] = self.octiron.graph

        return config

    def on_files(self, files: Files, config: Config):
        """Extract metadata from files and compose the site graph."""

        docs_dir = Path(config['docs_dir'])

        for mkdocs_file in files:
            mkdocs_file: File
            self.octiron.update_from_file(
                path=Path(mkdocs_file.abs_src_path),
                local_iri=src_path_to_iri(mkdocs_file.src_path),
                global_url=mkdocs_file.url,
            )

    def on_page_markdown(
        self,
        markdown: str,
        page: Page,
        config: Config,
        files: Files,
    ):
        """Inject page template path, if necessary."""
        template_name = get_template_by_page(
            page=page,
            graph=self.octiron.graph,
        )

        if template_name is not None:
            page.meta['template'] = template_name

        return markdown

    def on_page_context(
        self,
        context: TemplateContext,
        page: Page,
        config: Config,
        nav: Page,
    ) -> TemplateContext:
        """Attach the views to certain pages."""
        page_iri = rdflib.URIRef(
            f'{settings.LOCAL_IRI_SCHEME}{page.file.src_path}',
        )

        this_choices = list(map(
            operator.itemgetter(rdflib.Variable('this')),
            self.octiron.graph.query(
                'SELECT * WHERE { ?this octa:subjectOf ?page_iri }',
                initBindings={
                    'page_iri': page_iri,
                },
            ).bindings,
        ))

        if this_choices:
            context['this'] = this_choices[0]
        else:
            context['this'] = page_iri

        context['graph'] = self.octiron.graph
        context['iri'] = page_iri

        context['query'] = partial(
            query,
            instance=self.octiron.graph,
        )
        # FIXME this is hardcode, needs to be defined dynamically
        context['rdfs'] = rdflib.Namespace(
            'http://www.w3.org/2000/01/rdf-schema#',
        )

        return context

    def on_nav(
        self,
        nav: Navigation,
        config: Config,
        files: Files,
    ) -> Navigation:
        """Update the site's navigation from the knowledge graph."""
        return OctadocsNavigationProcessor(
            graph=self.octiron.graph,
            navigation=nav,
        ).generate()
