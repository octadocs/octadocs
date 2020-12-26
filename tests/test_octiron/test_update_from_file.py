from pathlib import Path

from rdflib import URIRef

from octiron import Octiron


def test_turtle():
    """Update Octiron graph from a Turtle file."""
    data_dir = Path(__file__).parent / 'data'

    octiron = Octiron(root_directory=data_dir)
    octiron.update_from_file(
        path=data_dir / 'rdfs.ttl',
        iri=URIRef('rdfs.ttl'),
    )
