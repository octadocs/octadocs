import functools
import sys
from dataclasses import dataclass
from typing import Dict, Iterable, List, NamedTuple, Optional, Union, cast

import rdflib
from mkdocs.structure.nav import (  # noqa: WPS450
    Link,
    Navigation,
    Section,
    _add_previous_and_next_links,
)
from mkdocs.structure.pages import Page
from octadocs.conversions import iri_by_page
from octadocs.query import SelectResult, query

if sys.version_info >= (3, 8):
    from functools import cached_property  # noqa
else:
    pass  # noqa: WPS420


NavigationItem = Union[Page, Section, Link, Navigation]

PAGE_DEFAULT_POSITION = 0


def is_index_md(navigation_item: NavigationItem) -> bool:
    """Determine if certain navigation item is an index.md page."""
    return (
        isinstance(navigation_item, Page) and
        navigation_item.file.src_path.endswith('index.md')
    )


class SortKey(NamedTuple):
    """Sort key."""

    is_index: bool
    position: int
    title: str


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


@functools.singledispatch
def create_pages_list_by_navigation(
    navigation_item: NavigationItem,
) -> Iterable[Page]:
    """Filter pages."""
    raise NotImplementedError()


@create_pages_list_by_navigation.register(Page)
def _create_pages_list_by_page(page: Page) -> Iterable[Page]:
    yield page


@create_pages_list_by_navigation.register(Section)
def _create_pages_list_by_section(section: Section) -> Iterable[Page]:
    for navigation_item in section.children:
        yield from create_pages_list_by_navigation(navigation_item)


@create_pages_list_by_navigation.register(Navigation)
def _create_pages_list_by_navigation(navigation: Navigation) -> Iterable[Page]:
    for navigation_item in navigation.items:
        yield from create_pages_list_by_navigation(navigation_item)


@dataclass(repr=False)
class OctadocsNavigationProcessor:
    """Rewrite navigation based on the knowledge graph."""

    graph: rdflib.ConjunctiveGraph
    navigation: Navigation

    @cached_property
    def position_by_page(self) -> Dict[rdflib.URIRef, int]:
        """Fetch the position by page from graph."""
        query_text = '''
            SELECT ?page ?position WHERE {
                ?page
                    a octa:Page ;
                    octa:position ?position .
            }
        '''

        rows = query(
            query_text=query_text,
            instance=self.graph,
        )

        return {
            row['page']: row['position'].value
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

    @functools.singledispatchmethod
    def rearrange_navigation(
        self,
        navigation_item: NavigationItem,
    ) -> NavigationItem:
        """Change the order of navigation menu elements."""
        raise NotImplementedError()

    @rearrange_navigation.register(Page)
    def _rearrange_page(self, page: Page) -> Page:
        iri = iri_by_page(page)
        position = self.position_by_page.get(
            iri,
            PAGE_DEFAULT_POSITION,
        )

        page.position = position
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

    @rearrange_navigation.register(Section)
    def _rearrange_section(self, section: Section) -> Section:
        section.children = self._rearrange_list_of_navigation_items(
            section.children,
        )

        index_page = find_index_page_in_section(section)
        if index_page is None:
            section.position = PAGE_DEFAULT_POSITION

        else:
            section.position = index_page.position

        return section

    @rearrange_navigation.register(Navigation)
    def _rearrange_navigation(self, navigation: Navigation):
        navigation.items = self._rearrange_list_of_navigation_items(
            navigation.items,
        )

        return navigation
