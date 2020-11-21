import json
from pathlib import Path
from typing import TypedDict

import frontmatter
import rdflib
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files, File
from rdflib.plugins.memory import IOMemory


class Config(TypedDict):
    """MkDocs configuration."""

    docs_dir: str


def update_graph_from_file(
    mkdocs_file: File,
    docs_dir: Path,
    universe: rdflib.ConjunctiveGraph,
):
    if not mkdocs_file.src_path.endswith('.md'):
        return None

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


class MetaPlugin(BasePlugin):
    """MkDocs Meta plugin."""

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

        raise Exception(list(universe))
