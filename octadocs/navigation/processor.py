import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, cast

import rdflib
# noinspection PyProtectedMember
from mkdocs.structure.nav import (  # noqa: WPS450
    Navigation,
    Section,
    _add_previous_and_next_links,
)
from mkdocs.structure.pages import Page
from octadocs.conversions import iri_by_page
from octadocs.navigation.nav_as_pages import create_pages_list_by_navigation
from octadocs.navigation.types import (
    PAGE_DEFAULT_POSITION,
    NavigationItem,
    SortKey,
)
from octadocs.query import SelectResult, query
from singledispatchmethod import singledispatchmethod

if sys.version_info >= (3, 8):
    from functools import cached_property  # noqa
else:
    from backports.cached_property import cached_property  # noqa: WPS433,WPS440


def is_index_md(navigation_item: NavigationItem) -> bool:
    """Determine if certain navigation item is an index.md page."""
    return (
        isinstance(navigation_item, Page) and
        navigation_item.file.src_path.endswith('index.md')
    )


def sort_key(navigation_item: NavigationItem) -> SortKey:
    """Determine sort key for a navigation item."""
    title = navigation_item.title
    if title is None:
        try:
            title = navigation_item.file.name
        except AttributeError:
            title = ''

    return SortKey(
        is_index=not is_index_md(navigation_item),
        position=navigation_item.position,
        title=title,
    )


def find_index_page_in_section(section: Section) -> Optional[Page]:
    """Find index.md page in the section, if any."""
    index_pages = list(filter(
        is_index_md,
        section.children,
    ))

    if index_pages:
        return index_pages[0]

    return None


@dataclass
class PageFromGraph:
    """Information about a Page retrieved from Octiron graph."""

    title: Optional[str] = None
    position: int = PAGE_DEFAULT_POSITION


@dataclass(repr=False)
class OctadocsNavigationProcessor:
    """Rewrite navigation based on the knowledge graph."""

    graph: rdflib.ConjunctiveGraph
    navigation: Navigation

    @cached_property
    def pages_from_graph(self) -> Dict[rdflib.URIRef, PageFromGraph]:
        """Fetch the position by page from graph."""
        query_text = '''
            SELECT ?page ?position ?title WHERE {
                ?page a octa:Page .
                ?thing octa:subjectOf ?page .

                OPTIONAL {
                    ?thing octa:position ?position .
                }

                OPTIONAL {
                    ?thing octa:title ?title .
                }
            }
        '''

        rows = query(
            query_text=query_text,
            instance=self.graph,
        )

        return {
            row['page']: PageFromGraph(
                title=getattr(
                    row.get('title'),
                    'value',
                    None,
                ),
                position=getattr(
                    row.get('position'),
                    'value',
                    PAGE_DEFAULT_POSITION,
                ),
            )
            for row in cast(SelectResult, rows)
        }

    def generate(self) -> Navigation:
        """Generate the navigation structure."""
        # Rearrange navigation itself
        navigation = self.rearrange_navigation(self.navigation)

        # Generate flat pages list
        pages = list(create_pages_list_by_navigation(navigation))
        navigation.pages = pages
        _add_previous_and_next_links(navigation.pages)

        return navigation

    @singledispatchmethod
    def rearrange_navigation(
        self,
        navigation_item: NavigationItem,
    ) -> NavigationItem:
        """Change the order of navigation menu elements."""
        raise NotImplementedError()

    @rearrange_navigation.register
    def _rearrange_page(self, page: Page) -> Page:
        iri = iri_by_page(page)
        page_from_graph = self.pages_from_graph.get(iri)

        if page_from_graph:
            page.title = page_from_graph.title
            page.position = page_from_graph.position

        else:
            page.position = PAGE_DEFAULT_POSITION

        return page

    def _rearrange_list_of_navigation_items(
        self,
        navigation_items: List[NavigationItem],
    ) -> List[NavigationItem]:
        navigation_items = list(map(
            self.rearrange_navigation,
            navigation_items,
        ))

        return sorted(
            navigation_items,
            key=sort_key,
        )

    @rearrange_navigation.register
    def _rearrange_section(self, section: Section) -> Section:
        section.children = self._rearrange_list_of_navigation_items(
            section.children,
        )

        index_page = find_index_page_in_section(section)
        if index_page is None:
            section.position = PAGE_DEFAULT_POSITION

        else:
            section.position = index_page.position

            if index_page.title:
                section.title = index_page.title

        return section

    @rearrange_navigation.register
    def _rearrange_navigation(self, navigation: Navigation):
        navigation.items = self._rearrange_list_of_navigation_items(
            navigation.items,
        )

        return navigation
