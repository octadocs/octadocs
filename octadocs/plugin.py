import json
from pathlib import Path
from typing import Dict, Any, Optional
from typing_extensions import TypedDict

import frontmatter
import owlrl
import rdflib
from boltons.iterutils import remap
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files, File
from mkdocs.structure.pages import Page
from pyld import jsonld

from octadocs import settings
from octadocs.conversions import src_path_to_iri
from rdflib.plugins.memory import IOMemory


class Extra(TypedDict):
    graph: rdflib.ConjunctiveGraph


class Config(TypedDict):
    """MkDocs configuration."""

    docs_dir: str
    extra: Optional[Extra]


class Context(TypedDict):
    """Context."""
    graph: Dict[str, Any]  # type: ignore


def update_graph_from_n3_file(
    mkdocs_file: File,
    docs_dir: Path,
    universe: rdflib.ConjunctiveGraph,
):
    universe.parse(
        source=str(docs_dir / mkdocs_file.src_path),
        format='n3',
        publicID=src_path_to_iri(mkdocs_file.src_path),
    )

    return universe


def convert_dollar_signs(meta_data):
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

    if meta_data.get('rdfs:isDefinedBy') is None:
        meta_data['rdfs:isDefinedBy'] = {
            '@id': page_id,
            'octa:url': mkdocs_file.url,
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

    serialized_meta_data = json.dumps(meta_data)

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


class OctaDocsPlugin(BasePlugin):
    """MkDocs Meta plugin."""

    graph: rdflib.ConjunctiveGraph = None

    def on_config(self, config: Config) -> Config:
        self.graph = rdflib.ConjunctiveGraph(store=IOMemory())
        self.graph.bind('octa', 'https://ns.octadocs.io/')
        self.graph.bind('schema', 'https://schema.org/')

        if config.get('extra') is None:
            config['extra'] = {}

        config['extra']['graph'] = self.graph

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

        owlrl.DeductiveClosure(owlrl.OWLRL_Extension).expand(self.graph)

    def on_page_context(
        self,
        context: Context,
        page: Page,
        config: Config,
        nav: Page,
    ) -> Context:
        """Attach the views to certain pages."""
        context['graph'] = self.graph
        return context
