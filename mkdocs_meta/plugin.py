import json
from pathlib import Path
from typing import TypedDict, Dict, Any

import frontmatter
import rdflib
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files, File
from mkdocs.structure.pages import Page
from pyld import jsonld
from rdflib.plugins.memory import IOMemory


class Config(TypedDict):
    """MkDocs configuration."""

    docs_dir: str


class Context(TypedDict):
    """Context."""
    zet: Dict[str, Any]  # type: ignore


def update_graph_from_n3_file(
    mkdocs_file: File,
    docs_dir: Path,
    universe: rdflib.ConjunctiveGraph,
):
    universe.parse(
        source=str(docs_dir / mkdocs_file.src_path),
        format='n3',
        publicID=mkdocs_file.src_path,
    )

    return universe


def update_graph_from_markdown_file(
    mkdocs_file: File,
    docs_dir: Path,
    universe: rdflib.ConjunctiveGraph,
):
    document = frontmatter.load(docs_dir / mkdocs_file.src_path)

    meta_data = document.metadata

    if not meta_data:
        return None

    meta_data.update({'@context': {
        '@vocab': 'kb://',
    }})

    if not meta_data.get('@id'):
        meta_data['@id'] = f'kb://{mkdocs_file.src_path}'

    universe.parse(
        data=json.dumps(meta_data),
        format='json-ld',
        publicID=mkdocs_file.src_path,
    )

    return universe


def update_graph_from_file(
    mkdocs_file: File,
    docs_dir: Path,
    universe: rdflib.ConjunctiveGraph,
):
    if mkdocs_file.src_path.endswith('.md'):
        return update_graph_from_markdown_file(
            mkdocs_file=mkdocs_file,
            docs_dir=docs_dir,
            universe=universe,
        )

    elif mkdocs_file.src_path.endswith('.n3'):
        return update_graph_from_n3_file(
            mkdocs_file=mkdocs_file,
            docs_dir=docs_dir,
            universe=universe,
        )

    return None


def get_view_content(ref: str, universe: rdflib.ConjunctiveGraph) -> str:
    """Render view content."""
    subgraph: rdflib.Graph = universe.query('''
        CONSTRUCT {
            ?thing <kb://title> ?label .
            ?thing <kb://category> ?category .
            ?thing <kb://description> ?description .
            rdfs: <kb://cards> ?thing .
        } WHERE {
            ?thing rdfs:isDefinedBy rdfs: .
            ?thing rdfs:label ?label .
            ?thing rdfs:comment ?description .
            ?thing <kb://category> ?category .
        }
    ''')

    # subgraph = universe.query('CONSTRUCT WHERE { ?s ?p ?o }')

    graph_dict = json.loads(subgraph.serialize(
        format='json-ld',
    ))

    frame = {
        '@context': {
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            '@vocab': 'kb://',
        },
        '@id': 'http://www.w3.org/2000/01/rdf-schema#',
    }

    graph_dict = jsonld.frame(graph_dict, frame)

    return graph_dict


class MetaPlugin(BasePlugin):
    """MkDocs Meta plugin."""

    universe: rdflib.ConjunctiveGraph = None

    def on_files(self, files: Files, config: Config):
        """Extract metadata from files and compose the site graph."""

        docs_dir = Path(config['docs_dir'])

        store = IOMemory()

        universe = rdflib.ConjunctiveGraph(store=store)

        for f in files:
            update_graph_from_file(
                mkdocs_file=f,
                docs_dir=docs_dir,
                universe=universe,
            )

        self.universe = universe

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

        view_content = get_view_content(ref, self.universe)

        context['zet'] = view_content
        # context['template'] = 'gallery.html'

        return context
