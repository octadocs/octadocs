import itertools

from octadocs.conversions import triples_to_quads
from octadocs.types import Triple
from owlrl import OWLRL_Extension
from rdflib import URIRef


class OWLRLExtensionNamedGraph(OWLRL_Extension):
    """OWL RL with inferred triples in a separate graph."""

    graph_name = URIRef('inference')

    def flush_stored_triples(self):
        """Store the triples into a named graph."""
        # Remove the previous version of inferences
        self.graph.remove_context(self.graph_name)

        triples = itertools.starmap(
            Triple,
            self.added_triples,
        )
        quads = triples_to_quads(triples, graph=self.graph_name)
        self.graph.addN(quads)

        self.empty_stored_triples()
