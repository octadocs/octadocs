import json
import logging
import operator
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union

import frontmatter
import owlrl
import rdflib
from boltons.iterutils import remap
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files
from mkdocs.structure.nav import Navigation, Section
from mkdocs.structure.pages import Page
from pyld import jsonld
from rdflib.plugins.memory import IOMemory
from typing_extensions import TypedDict

from octadocs import settings
from octadocs.environment import query, src_path_to_iri
from octadocs.navigation import OctadocsNavigationProcessor

NavigationItem = Union[Page, Section]

MetaData = Dict[str, Any]   # type: ignore

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


def convert_dollar_signs(
    meta_data: MetaData,
) -> MetaData:
    """
    Convert $ character to @ in keys.

    We use $ by convention to avoid writing quotes.
    """
    return remap(
        meta_data,
        lambda path, key, value: (
            key.replace('$', '@') if isinstance(key, str) else key,
            value,
        ),
    )


def update_graph_from_markdown_file(
    mkdocs_file: File,
    docs_dir: Path,
    universe: rdflib.ConjunctiveGraph,
    context: Dict[str, str],
):
    document = frontmatter.load(docs_dir / mkdocs_file.src_path)

    meta_data = document.metadata

    if not meta_data:
        return None

    meta_data = convert_dollar_signs(meta_data)

    meta_data.update({'@context': context})

    page_id = src_path_to_iri(mkdocs_file.src_path)

    if meta_data.get('@id') is None:
        meta_data['@id'] = page_id

    if meta_data.get('octa:subjectOf') is None:
        meta_data['octa:subjectOf'] = {
            '@id': page_id,
            'octa:url': f'/{mkdocs_file.url}',
            '@type': 'octa:Page',
        }

    # Reason: https://github.com/RDFLib/rdflib-jsonld/issues/97
    # If we don't expand with an explicit @base, import will fail silently.
    meta_data = jsonld.expand(
        meta_data,
        options={
            'base': settings.LOCAL_IRI_SCHEME,
        },
    )

    # Reason: https://github.com/RDFLib/rdflib-jsonld/issues/98
    # If we don't flatten, @included sections will not be imported.
    meta_data = jsonld.flatten(meta_data)

    serialized_meta_data = json.dumps(meta_data, indent=4)

    universe.parse(
        data=serialized_meta_data,
        format='json-ld',
        publicID=page_id,
    )

    return universe


def update_graph_from_file(
    mkdocs_file: File,
    docs_dir: Path,
    universe: rdflib.ConjunctiveGraph,
    context: Dict[str, str],
):
    if mkdocs_file.src_path.endswith('.md'):
        return update_graph_from_markdown_file(
            mkdocs_file=mkdocs_file,
            docs_dir=docs_dir,
            universe=universe,
            context=context,
        )

    elif mkdocs_file.src_path.endswith('.n3'):
        return update_graph_from_n3_file(
            mkdocs_file=mkdocs_file,
            docs_dir=docs_dir,
            universe=universe,
        )

    return None


def fetch_context(docs_dir: Path) -> Dict[str, str]:
    """Compose JSON-LD context."""
    with open(docs_dir / 'context.json', 'r') as context_file:
        json_document = json.load(context_file)

    json_document.update({
        '@vocab': settings.LOCAL_IRI_SCHEME,
        '@base': settings.LOCAL_IRI_SCHEME,
    })

    return json_document


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


def apply_inference_in_place(
    graph: rdflib.ConjunctiveGraph,
    docs_dir: Path,
) -> None:
    """Apply inference rules."""
    logger.info('Inference: OWL RL')
    owlrl.DeductiveClosure(owlrl.OWLRL_Extension).expand(graph)

    # Fill in octa:about relationships.
    logger.info(
        'Inference: ?thing octa:subjectOf ?page ⇒ ?page octa:about ?thing .',
    )
    graph.update('''
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
    graph.update('''
        INSERT {
            ?page octa:title ?title .
        } WHERE {
            ?subject
                rdfs:label ?title ;
                octa:subjectOf ?page .
        }
    ''')

    inference_dir = docs_dir.parent / 'inference'
    if inference_dir.is_dir():
        for sparql_file in inference_dir.iterdir():
            logger.info('Inference: %s', sparql_file.name)
            sparql_text = sparql_file.read_text()
            graph.update(sparql_text)


class OctaDocsPlugin(BasePlugin):
    """MkDocs Meta plugin."""

    graph: rdflib.ConjunctiveGraph = None

    def on_config(self, config: Config) -> Config:
        self.graph = rdflib.ConjunctiveGraph(store=IOMemory())

        self.graph.bind('octa', 'https://ns.octadocs.io/')
        self.graph.bind('schema', 'https://schema.org/')
        self.graph.bind('local', 'local')

        if config.get('extra') is None:
            config['extra'] = {'graph': self.graph}

        else:
            config['extra'].update(  # type: ignore
                graph=self.graph,
            )

        return config

    def on_files(self, files: Files, config: Config):
        """Extract metadata from files and compose the site graph."""

        docs_dir = Path(config['docs_dir'])
        context = fetch_context(docs_dir)

        for f in files:
            update_graph_from_file(
                mkdocs_file=f,
                docs_dir=docs_dir,
                universe=self.graph,
                context=context,
            )

        apply_inference_in_place(self.graph, docs_dir=docs_dir)

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
            graph=self.graph,
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
            self.graph.query(
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

        context['graph'] = self.graph
        context['iri'] = page_iri

        context['query'] = partial(
            query,
            instance=self.graph,
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
            graph=self.graph,
            navigation=nav,
        ).generate()
