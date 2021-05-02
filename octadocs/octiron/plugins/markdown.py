from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List

import frontmatter
import rdflib
from documented import DocumentedError
from octadocs.octiron.plugins import Loader
from octadocs.octiron.yaml_extensions import as_triple_stream
from octadocs.types import OCTA, Triple
from yaml.scanner import ScannerError


@dataclass
class InvalidFrontmatter(DocumentedError):
    """
    Markdown Front Matter is not a valid YAML document.

    Path: {self.path}

    Read raw front matter below:

    {self.raw_frontmatter}

    Error:

    {self.error}

    {self.explanation}
    """   # noqa

    path: Path
    raw_frontmatter: str
    error: ScannerError

    @property
    def explanation(self) -> str:
        """Explain the error to the user."""
        if 'found character \'\\t\' that' in str(self.error):   # noqa: WPS342
            return 'Suggestion:\n  Use spaces, not tabs, for indentation.'

        if self.error.problem == 'mapping values are not allowed here':
            return (
                'Suggestion:\n'
                '  If property value contains ":", use quotes.\n\n'
                '  Bad:\n\n'
                '    label: FP for Sceptics: Intuitive guide to map/flatmap\n\n'
                '  Good:\n\n'
                '    label: "FP for Sceptics: Intuitive guide to map/flatmap"'
            )

        return ''


def process_yaml_scanner_error(
    err: ScannerError,
    path: Path,
) -> InvalidFrontmatter:
    """Process YAML error and explain it to the user."""
    # Read the head of the file to print it in the error message
    raw_frontmatter: List[str] = []
    with path.open() as raw_file:
        for line in raw_file:
            if len(raw_frontmatter) > 10:
                raw_frontmatter.append('...')
                break

            if line.startswith('---') and raw_frontmatter:
                raw_frontmatter.append(line.strip('\n'))
                break

            raw_frontmatter.append(line.strip('\n'))

    return InvalidFrontmatter(
        path=path,
        raw_frontmatter='\n'.join(raw_frontmatter),
        error=err,
    )


class MarkdownLoader(Loader):
    """Load semantic data from Markdown front matter."""

    regex = r'\.md$'

    def stream(self) -> Iterator[Triple]:
        """Return stream of triples."""
        try:
            meta_data = frontmatter.load(self.path).metadata
        except ScannerError as err:
            raise process_yaml_scanner_error(
                err=err,
                path=self.path,
            ) from err

        yield from as_triple_stream(
            raw_data=meta_data,
            context=self.context,
            local_iri=self.local_iri,
        )

        # The IRI of the local page is a page.
        # FIXME: maybe this should be in octiron.py and work globally.
        yield Triple(self.local_iri, rdflib.RDF.type, OCTA.Page)

        # The page will be available on the Web under certain URL.
        if self.global_url is not None:
            yield Triple(
                self.local_iri,
                OCTA.url,
                rdflib.Literal(self.global_url),
            )
