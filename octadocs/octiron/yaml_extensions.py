from typing import Any, Dict

from boltons.iterutils import remap

MetaData = Dict[str, Any]   # type: ignore


def _convert(term: Any) -> Any:  # type: ignore
    """Convert $statement to @statement."""
    if isinstance(term, str) and term.startswith('$'):
        return '@' + term[1:]  # noqa: WPS336

    return term


def convert_dollar_signs(
    meta_data: MetaData,
) -> MetaData:
    """
    Convert $ character to @ in keys.

    We use $ by convention to avoid writing quotes.
    """
    return remap(
        meta_data,
        lambda path, key, value: (  # noqa: WPS110
            _convert(key),
            _convert(value),
        ),
    )
