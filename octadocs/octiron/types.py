from types import MappingProxyType
from typing import Any, Dict, NamedTuple, Optional, Union

import rdflib

OCTA = rdflib.Namespace('https://ns.octadocs.io/')
LOCAL = rdflib.Namespace('local:')


# To prevent WPS401 Found mutable module constant
DEFAULT_NAMESPACES = MappingProxyType({
    'octa': OCTA,
    'local': LOCAL,
    '': LOCAL,

    'rdf': rdflib.RDF,
    'rdfs': rdflib.RDFS,
    'xsd': rdflib.XSD,
    'schema': rdflib.SDO,
    'sh': rdflib.SH,
    'skos': rdflib.SKOS,
    'owl': rdflib.OWL,
    'dc': rdflib.DC,
    'dcat': rdflib.DCAT,
    'dcterms': rdflib.DCTERMS,
    'foaf': rdflib.FOAF,
})


class Triple(NamedTuple):
    """RDF triple."""

    subject: rdflib.URIRef
    predicate: rdflib.URIRef
    object: Union[rdflib.URIRef, rdflib.Literal]  # noqa: WPS125

    def as_quad(self, graph: rdflib.URIRef) -> 'Quad':
        """Add graph to this triple and hence get a quad."""
        return Quad(self.subject, self.predicate, self.object, graph)


class Quad(NamedTuple):
    """Triple assigned to a named graph."""

    subject: rdflib.URIRef
    predicate: rdflib.URIRef
    object: Union[rdflib.URIRef, rdflib.Literal]  # noqa: WPS125
    graph: rdflib.URIRef


# Should be Dict[str, 'Context'] but mypy crashes on a recursive type.
Context = Optional[   # type: ignore
    Union[str, int, float, Dict[str, Any]],
]
