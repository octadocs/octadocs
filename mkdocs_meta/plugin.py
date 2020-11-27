import json
from pathlib import Path
from typing import TypedDict, Dict, Any, Optional

import frontmatter
import rdflib
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files, File
from mkdocs.structure.pages import Page
from rdflib import URIRef
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
        publicID=f'kb://{mkdocs_file.src_path}',
    )

    return universe


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

    meta_data.update({'@context': context})

    page_id = f'kb://{mkdocs_file.url}'

    if meta_data.get('@id') is None:
        meta_data['@id'] = page_id

    if meta_data.get('rdfs:isDefinedBy') is None:
        meta_data['rdfs:isDefinedBy'] = page_id

    universe.parse(
        data=json.dumps(meta_data),
        format='json-ld',
        publicID=f'kb://{mkdocs_file.url}',
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

    if json_document.get('@vocab') is None:
        json_document.update({
            '@vocab': 'kb://',
        })

    return json_document


class MetaPlugin(BasePlugin):
    """MkDocs Meta plugin."""

    graph: rdflib.ConjunctiveGraph = None

    def on_config(self, config: Config) -> Config:
        self.graph = rdflib.ConjunctiveGraph(store=IOMemory())

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

    def on_page_context(
        self,
        context: Context,
        page: Page,
        config: Config,
        nav: Page,
    ) -> Context:
        """Attach the views to certain pages."""
        ref = f'kb://{page.url}'

        if ref.endswith('/'):
            ref += 'index.md'

        context['graph'] = self.graph

        page.meta['graph'] = self.graph

        return context
