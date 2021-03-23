import logging
from dataclasses import dataclass

from mkdocs.structure.nav import Navigation, Section
from mkdocs.structure.pages import Page
from octadocs.conversions import iri_by_page
from octadocs.navigation.processor import find_index_page_in_section
from octadocs.navigation.types import NavigationItem
from octadocs.octiron.types import LOCAL, OCTA
from rdflib import ConjunctiveGraph, URIRef
from singledispatchmethod import singledispatchmethod

logger = logging.getLogger(__name__)


@dataclass
class NavigationToGraphReader:
    """Read navigation tree into graph."""

    graph: ConjunctiveGraph
    navigation_graph_iri: URIRef = LOCAL.navigation

    def create_parent_link(
        self,
        child_iri: URIRef,
        parent_iri: URIRef,
    ) -> None:
        """Mark one IRI as parent of the other."""
        self.graph.add((
            parent_iri,
            OCTA.isParentOf,
            child_iri,
            self.navigation_graph_iri,
        ))

    @singledispatchmethod
    def update_graph(self, navigation_item: NavigationItem) -> None:
        """Default implementation is not available."""
        raise NotImplementedError(
            f'{navigation_item} is not a supported element.',
        )

    @update_graph.register
    def _update_graph_from_navigation(self, navigation: Navigation) -> None:
        """Read the whole navigation tree."""
        self.graph.update(f'CLEAR GRAPH <{self.navigation_graph_iri}>')
        for navigation_item in navigation.items:
            self.update_graph(
                navigation_item,
                parent_iri=URIRef(LOCAL),
            )

    @update_graph.register
    def _update_graph_from_page(
        self,
        page: Page,
        parent_iri: URIRef,
    ) -> None:
        """Read information about a Page into the graph."""
        iri = iri_by_page(page)
        self.create_parent_link(iri, parent_iri)

    @update_graph.register
    def _update_graph_from_section(
        self,
        section: Section,
        parent_iri: URIRef,
    ) -> None:
        """Read information about a Section into the graph."""
        index_page = find_index_page_in_section(section)
        if index_page is None:
            logger.warning(
                'The section {section} does not have an index.md file in it. '
                'Cannot read its structure into Octadocs graph.',
                extra={
                    'section': section,
                },
            )
            return

        iri = iri_by_page(index_page)

        self.update_graph(
            index_page,
            parent_iri=parent_iri,
        )

        for navigation_item in section.children:
            if navigation_item != index_page:
                self.update_graph(
                    navigation_item,
                    parent_iri=iri,
                )
