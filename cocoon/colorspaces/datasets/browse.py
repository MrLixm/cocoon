__all__ = (
    "get_available_colorspaces",
    "get_available_colorspaces_names",
    "get_available_colorspaces_names_aliases",
    "get_colorspace",
)

import contextlib
from typing import Optional

from cocoon.colorspaces import RgbColorspace
from cocoon.colorspaces.datasets._build import _COLORSPACES


_COLORSPACES_KEYS_DISABLED: list[str] = []


def _colorspaces_dataset():
    """
    Get the dataset of enabled colorspace.
    """
    # not a deepcopy, we want to keep the same instances
    dataset = _COLORSPACES.copy()
    [dataset.pop(key) for key in _COLORSPACES_KEYS_DISABLED]
    return dataset


@contextlib.contextmanager
def disable_colorspaces(names: list[str]):
    """
    Make the given colorspaces innacessible via the get functions.

    Nesting context is cummulative (disable upon the previously disable colorspaces).

    Examples:

        >>> import cocoon
        >>> assert cocoon.get_colorspace("sRGB") is not None
        >>> with disable_colorspaces(["sRGB"]):
        >>>     assert cocoon.get_colorspace("sRGB") is None
        >>> assert cocoon.get_colorspace("sRGB") is not None

    Args:
        names: list of valid colorspaces names/alias to disable
    """
    global _COLORSPACES_KEYS_DISABLED
    previous_disabled = _COLORSPACES_KEYS_DISABLED.copy()

    for colorspace_name in names:
        colorspace = _COLORSPACES[colorspace_name]
        aliases = _get_colorspace_aliases(colorspace)
        _COLORSPACES_KEYS_DISABLED.extend(aliases)

    try:
        yield
    finally:
        _COLORSPACES_KEYS_DISABLED = previous_disabled


def _get_colorspace_aliases(colorspace: RgbColorspace) -> list[str]:
    """
    Get all the aliases name that allow to retrive the given colorspace.
    """
    aliases = []

    for colorspace_item_name, colorspace_item in _colorspaces_dataset().items():
        if colorspace != colorspace_item:
            continue
        aliases.append(colorspace_item_name)

    return aliases


def get_available_colorspaces() -> list[RgbColorspace]:
    """
    List of RgbColorspace with no duplicates and sorted alphabetically by name.
    """

    def get_colorspace_name(colorspace: RgbColorspace):
        return colorspace.name

    return sorted(
        list(set(_colorspaces_dataset().values())),
        key=get_colorspace_name,
    )


def get_available_colorspaces_names() -> list[str]:
    """
    List of colorspace indentifier that correspond to a colorspace.
    No duplicates and sorted alphabetically by name.
    """
    return sorted(list(set(_colorspaces_dataset().keys())))


def get_available_colorspaces_names_aliases() -> list[tuple[str]]:
    """
    Get all the colorspaces available as tuple of the different alias
    corresponding to a same colorspace.

    Example::

        [("ProPhoto RGB", "prophoto-rgb", "prophoto"), ...]

    Returns:
        list of colorspaces names available as a tuple of aliases
    """

    buffer_dict = {}

    for colorspace_name, colorspace in _colorspaces_dataset().items():
        identifier = hash(colorspace)

        if buffer_dict.get(identifier):
            buffer_dict[identifier].append(colorspace_name)
        else:
            buffer_dict[identifier] = [colorspace_name]

    return [tuple(name_tuple) for name_tuple in buffer_dict.values()]


def get_colorspace(
    name: Optional[str],
    force_linear: bool = False,
) -> Optional[RgbColorspace]:
    """
    Retrieve the colour colorspace instance corresponding to the given name.

    # TODO is force_linear really necessary ?

    Args:
        name: literal name of the colourspace or one of its available alias
        force_linear:
            True to return a colorspace with linear transfer-functions. Even if not
            originally designed with those.

    Returns:
        colorspace instance or None if not found.
    """
    if not name:
        return None

    colorspace = _colorspaces_dataset().get(name)
    if not colorspace:
        return None

    if force_linear:
        colorspace = colorspace.as_linear_copy()

    return colorspace
