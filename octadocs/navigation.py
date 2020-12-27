import sys
from dataclasses import dataclass
from typing import Union

import rdflib
from mkdocs.structure.nav import Navigation, Section
from mkdocs.structure.pages import Page

from octadocs.conversions import get_page_title_by_iri, iri_by_page

if sys.version_info >= (3, 8):
    from functools import cached_property  # noqa
else:
    from backports.cached_property import cached_property  # noqa: WPS433,WPS440


NavigationItem = Union[Page, Section]


@dataclass(repr=False)
class OctadocsNavigationProcessor:
    """Rewrite navigation based on the knowledge graph."""

    graph: rdflib.ConjunctiveGraph
    navigation: Navigation

    @cached_property
    def homepage(self) -> Page:
        """Find the home page of the documentation site."""
        (home_page, ) = filter(
            lambda navigation_item: (
                isinstance(navigation_item, Page) and
                navigation_item.is_homepage
            ),
            self.navigation.items,
        )

        return home_page

    def generate(self) -> Navigation:
        """Generate the navigation structure."""
        navigation_items = list(map(
            self._process_nav_item,
            self.navigation.items,
        ))

        self.navigation.items = navigation_items

        return self.navigation

    def _process_nav_item(self, item: NavigationItem) -> NavigationItem:
        if isinstance(item, Page):
            return self._process_nav_page(item)

        elif isinstance(item, Section):
            return self._process_nav_section(item)

        else:
            raise Exception(f'What the heck is {item}?')

    def _process_nav_page(self, page: Page) -> Page:
        """Add title to a page."""
        iri = iri_by_page(page)

        title = get_page_title_by_iri(
            iri=iri,
            graph=self.graph,
        )

        if title:
            page.title = title

        return page

    def _process_nav_section(self, section: Section) -> NavigationItem:
        """Process section."""
        section.children = list(map(
            self._process_nav_item,
            section.children,
        ))

        if len(section.children) == 1:
            index_page = section.children[0]
            index_page.parent = section.parent
            return index_page

        index_page_candidates = list(filter(
            lambda page: page.file.src_path.endswith('index.md'),
            section.children,
        ))

        if index_page_candidates:
            index_page = index_page_candidates[0]
            section.title = index_page.title

            if section.parent is not None:
                index_page.parent = section.parent

        return section
