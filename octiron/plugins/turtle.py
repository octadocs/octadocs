from octiron.plugins.base import OctironPlugin


class TurtlePlugin(OctironPlugin):
    """Read data from Turtle files."""

    regex = r'\.ttl$'
