import functools
import sys
from dataclasses import dataclass
from typing import Union, NamedTuple

import rdflib
from mkdocs.structure.nav import Link, Navigation, Section
from mkdocs.structure.pages import Page

from octadocs.conversions import iri_by_page
from octadocs.query import query

if sys.version_info >= (3, 8):
    from functools import cached_property  # noqa
else:
    pass


NavigationItem = Union[Page, Section, Link]


def is_index_md(navigation_item: NavigationItem) -> bool:
    """Determine if certain navigation item is an index.md page."""
    return (
        isinstance(navigation_item, Page) and
        navigation_item.file.src_path.endswith('index.md')
    )


@functools.singledispatch
def assign_position_and_reorder(
    navigation_item: NavigationItem,
    graph: rdflib.ConjunctiveGraph,
) -> NavigationItem:
    """Get position for a navigation item from the graph."""
    raise NotImplementedError(f'Cannot get position for: {navigation_item}')


@assign_position_and_reorder.register(Page)
def _get_position_page(page: Page, graph: rdflib.ConjunctiveGraph) -> Page:
    """Fetch octa:position for a given Page."""
    rows = query(
        query_text='''
            SELECT ?position WHERE {
                ?iri octa:position ?position .
            }
        ''',
        instance=graph,
        iri=iri_by_page(page),
    )

    position = rows[0]['position'] if rows else 0

    page.position = position

    return page


class SortKey(NamedTuple):
    """Sort key."""

    position: int
    title: str


def sort_key(navigation_item: NavigationItem) -> SortKey:
    """Determine sort key for a navigation item."""
    return SortKey(
        position=navigation_item.position,
        title=navigation_item.title,
    )


@assign_position_and_reorder.register(Section)
@assign_position_and_reorder.register(Navigation)
def _get_position_section(
    section: Section,
    graph: rdflib.ConjunctiveGraph,
) -> Section:
    """Fetch octa:position for a section."""
    section.children = [
        assign_position_and_reorder(child, graph)
        for child in section.children
    ]

    section.children.sort(
        key=sort_key,
    )

    index_pages = list(filter(
        is_index_md,
        section.children,
    ))

    position = index_pages[0].position if index_pages else 0

    section.position = position

    return section


@dataclass(repr=False)
class OctadocsNavigationProcessor:
    """Rewrite navigation based on the knowledge graph."""

    graph: rdflib.ConjunctiveGraph
    navigation: Navigation

    def generate(self) -> Navigation:
        """Generate the navigation structure."""
        return assign_position_and_reorder(self.navigation)

    def _process_nav_item(self, item: NavigationItem) -> NavigationItem:
        if isinstance(item, Page):
            return self._process_nav_page(item)

        elif isinstance(item, Section):
            return self._process_nav_section(item)

        elif isinstance(item, Link):
            return item

        return item

    def _process_nav_page(self, page: Page) -> Page:
        """Process a page."""
        return page

    def _process_nav_section(self, section: Section) -> NavigationItem:
        """Process section."""
        # return assign_position_and_reorder()
