from typing import Dict, Any

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
        lambda path, key, value: (
            key.replace('$', '@') if isinstance(key, str) else key,
            value,
        ),
    )
