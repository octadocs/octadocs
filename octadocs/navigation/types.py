from typing import NamedTuple, Union

from mkdocs.structure.nav import Link, Navigation, Section
from mkdocs.structure.pages import Page

NavigationItem = Union[Page, Section, Link, Navigation]
PAGE_DEFAULT_POSITION = 0


class SortKey(NamedTuple):
    """Sort key."""

    is_index: bool
    position: int
    title: str
