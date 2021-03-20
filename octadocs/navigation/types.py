from typing import Union, NamedTuple

from mkdocs.structure.nav import Section, Link, Navigation
from mkdocs.structure.pages import Page

NavigationItem = Union[Page, Section, Link, Navigation]
PAGE_DEFAULT_POSITION = 0


class SortKey(NamedTuple):
    """Sort key."""

    is_index: bool
    position: int
    title: str
