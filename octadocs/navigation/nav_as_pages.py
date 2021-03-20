import functools
from typing import Iterable

from mkdocs.structure.nav import Navigation, Section
from mkdocs.structure.pages import Page
from octadocs.navigation.types import NavigationItem


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
