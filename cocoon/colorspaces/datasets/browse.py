__all__ = (
    "get_available_colorspaces",
    "get_available_colorspaces_names",
    "get_available_colorspaces_names_aliases",
    "get_colorspace",
)

from typing import Optional

from cocoon.colorspaces import RgbColorspace
from cocoon.colorspaces.datasets.build import _COLORSPACES


def get_available_colorspaces() -> list[RgbColorspace]:
    """
    List of RgbColorspace with no duplicates and sorted alphabetically by name.
    """

    def get_colorspace_name(colorspace: RgbColorspace):
        return colorspace.name

    return sorted(
        list(set(_COLORSPACES.values())),
        key=get_colorspace_name,
    )


def get_available_colorspaces_names() -> list[str]:
    """
    List of colorspace indentifier that correspond to a colorspace.
    No duplicates and sorted alphabetically by name.
    """
    return sorted(list(set(_COLORSPACES.keys())))


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

    for colorspace_name, colorspace in _COLORSPACES.items():
        identifier = hash(colorspace)

        if buffer_dict.get(identifier):
            buffer_dict[identifier].append(colorspace_name)
        else:
            buffer_dict[identifier] = [colorspace_name]

    return [tuple(name_tuple) for name_tuple in buffer_dict.values()]


def get_colorspace(name: Optional[str]) -> Optional[RgbColorspace]:
    """
    Retrieve the colour colorspace instance corresponding to the given name.

    You can ask a linear variant of the colorspace by suffixing the name with ``:linear``

    Args:
        name: literal name of the colourspace or one of its available alias

    Returns:
        colorspace instance or None if not found.
    """
    if not name:
        return None

    linear_asked = name.endswith(":linear")
    name = name.removesuffix(":linear")

    colorspace = _COLORSPACES.get(name)
    if not colorspace:
        return None

    if linear_asked:
        colorspace = colorspace.as_linear_copy()

    return colorspace
