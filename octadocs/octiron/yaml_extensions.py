from typing import Any, Dict

from boltons.iterutils import remap

MetaData = Dict[str, Any]   # type: ignore


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
            key.replace('$', '@') if isinstance(key, str) else key,
            value,
        ),
    )
