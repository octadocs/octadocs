from typing import Tuple, Union, NewType, NamedTuple

import rdflib


class Triple(NamedTuple):
    """RDF triple."""

    subject: rdflib.URIRef
    predicate: rdflib.URIRef
    object: Union[rdflib.URIRef, rdflib.Literal]
