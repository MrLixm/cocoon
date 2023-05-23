import logging
from typing import Optional

import numpy

from cocoon.colorspaces import RgbColorspace
from cocoon.colorspaces import get_available_colorspaces

exr_chromaticities_type = tuple[float, float, float, float, float, float, float, float]
"""
Tuple of values as (R.x, R.y, G.x, G.y, B.x, B.y, whitepoint.x, whitepoint.y) where
``x`` and ``y`` are CIE x,y coordinates.
"""

exr_chromaticities_XYZ: exr_chromaticities_type = (1, 0, 0, 1, 0, 0, 1 / 3, 1 / 3)
"""
References:
   - [1] https://openexr.readthedocs.io/en/latest/TechnicalIntroduction.html#cie-xyz-color
"""


def exr_chromaticities_to_colorspace(
    exr_chromaticities: exr_chromaticities_type,
    ensure_linear_cctf: bool = True,
) -> list[RgbColorspace]:
    """
    Convert OpenEXR ``chromaticities`` attribute to pontential RgbColorspace instances.

    It's possible that multiple matching colorspaces are found as they can only
    differ in transfer-functions, which are not specified in the attribute.

    References:
       - [1] https://openexr.readthedocs.io/en/latest/TechnicalIntroduction.html#rgb-color

    Args:
       exr_chromaticities:
            chromaticities attribute as defined in the OpenEXR spec.
            (R.x, R.y, G.x, G.y, B.x, B.y, whitepoint.x, whitepoint.y)
       ensure_linear_cctf:
            If True make sure the returned colorspace instance use a linear transfer-function
            only if that not already the case.
            If False, the instance might or might not use a linear cctf.
            The OpenEXR spec imply this should be True by default.

    Returns:
        list of RgbColorspace that should match the given chromaticities.
    """
    colorspace_list = []

    # not supported currently
    if exr_chromaticities == exr_chromaticities_XYZ:
        return colorspace_list

    exr_whitepoint = numpy.array(exr_chromaticities[-2:])
    exr_primaries = numpy.array(exr_chromaticities[:-2])
    exr_primaries = exr_primaries.reshape((3, 2))

    for colorspace in get_available_colorspaces():
        if colorspace.whitepoint is None or colorspace.gamut is None:
            continue

        if not numpy.allclose(exr_whitepoint, colorspace.whitepoint.coordinates):
            continue

        if not numpy.allclose(exr_primaries, colorspace.gamut.primaries):
            continue

        if ensure_linear_cctf and not colorspace.transfer_functions.are_linear:
            colorspace_list.append(colorspace.as_linear_copy())
        else:
            colorspace_list.append(colorspace)

    return colorspace_list


def colorspace_to_exr_chromaticities(
    colorspace: RgbColorspace,
) -> Optional[exr_chromaticities_type]:
    """
    Convert the given RgbColorspace to the OpenEXR ``chromaticities`` attribute.

    Structured as ``(R.x, R.y, G.x, G.y, B.x, B.y, whitepoint.x, whitepoint.y)``

    Args:
       colorspace: source colorspace to generate the attribute from

    References:
       - [1] https://openexr.readthedocs.io/en/latest/TechnicalIntroduction.html#rgb-color

    Returns:
        chromaticities attribute as defined in the OpenEXR spec or None if not possible.
    """
    if colorspace.gamut is None or colorspace.whitepoint is None:
        return None

    # noinspection PyTypeChecker
    primaries: list[float] = numpy.concatenate(colorspace.gamut.primaries, -1).tolist()
    # noinspection PyTypeChecker
    whitepoint: list[float] = colorspace.whitepoint.coordinates.tolist()
    # noinspection PyTypeChecker
    return *primaries, *whitepoint
