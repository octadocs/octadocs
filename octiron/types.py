from typing import Union, NamedTuple, Dict, Optional

import rdflib


OCTA = rdflib.Namespace('https://ns.octadocs.io/')
LOCAL = rdflib.Namespace('local:')


class Triple(NamedTuple):
    """RDF triple."""

    subject: rdflib.URIRef
    predicate: rdflib.URIRef
    object: Union[rdflib.URIRef, rdflib.Literal]

    def as_quad(self, graph: rdflib.URIRef) -> 'Quad':
        """Add graph to this triple and hence get a quad."""
        return Quad(self.subject, self.predicate, self.object, graph)


class Quad(NamedTuple):
    """Triple assigned to a named graph."""

    subject: rdflib.URIRef
    predicate: rdflib.URIRef
    object: Union[rdflib.URIRef, rdflib.Literal]
    graph: rdflib.URIRef


Context = Optional[Union[str, int, float, Dict[str, 'Context']]]
