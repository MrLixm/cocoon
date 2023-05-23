__all__ = (
    "matrix_chromatic_adaptation_transform",
    "matrix_colorspace_to_colorspace",
    "colorspace_to_XYZ",
    "colorspace_to_colorspace",
    "XYZ_to_colorspace",
)

import functools
from typing import Optional

import colour
import numpy

from cocoon.colorspaces import RgbColorspace
from cocoon.colorspaces import Whitepoint
from cocoon.colorspaces import ChromaticAdaptationTransform


@functools.lru_cache
def matrix_chromatic_adaptation_transform(
    source_whitepoint: Whitepoint,
    target_whitepoint: Whitepoint,
    transform_name: ChromaticAdaptationTransform,
):
    """
    Return the 3x3 matrix to convert the given illuminant to teh target illuminant
    using the given transform name.

    Args:
        source_whitepoint:
        target_whitepoint:
        transform_name:

    Returns:
        3x3 matrix
    """
    return colour.adaptation.matrix_chromatic_adaptation_VonKries(
        colour.models.xy_to_XYZ(source_whitepoint.coordinates),
        colour.models.xy_to_XYZ(target_whitepoint.coordinates),
        str(transform_name.value),
    )


def matrix_colorspace_to_colorspace(
    source_colorspace: RgbColorspace,
    target_colorspace: RgbColorspace,
    chromatic_adaptation_transform: Optional[ChromaticAdaptationTransform],
) -> numpy.ndarray:
    """
    Compute the matrix :math:`M` converting from given input *RGB*
    colourspace to output *RGB* colourspace using given *chromatic
    adaptation* method.

    Note:
        shameless copy of colour.matrix_RGB_to_RGB()

    Args:
        source_colorspace:
        target_colorspace:
        chromatic_adaptation_transform: for whitepoint conversion

    Returns:
        a 3x3 matrix for the conversion between the 2 given colorspaces.
    """
    if (
        source_colorspace.is_no_op
        or target_colorspace.is_no_op
        or not source_colorspace.gamut
        or not target_colorspace.gamut
    ):
        return numpy.identity(3)

    M = source_colorspace.matrix_to_XYZ

    if (
        chromatic_adaptation_transform is not None
        and not source_colorspace.whitepoint
        or not target_colorspace.whitepoint
    ):
        raise ValueError(
            f"missing whitepoint on one of the colorspace argument: "
            f"source_colorspace {source_colorspace.whitepoint}, "
            f"target_colorspace {target_colorspace.whitepoint}"
        )

    if chromatic_adaptation_transform is not None:
        M_CAT = matrix_chromatic_adaptation_transform(
            source_colorspace.whitepoint,
            target_colorspace.whitepoint,
            chromatic_adaptation_transform,
        )

        M = colour.algebra.matrix_dot(M_CAT, source_colorspace.matrix_to_XYZ)

    M = colour.algebra.matrix_dot(target_colorspace.matrix_from_XYZ, M)

    return M


def colorspace_to_XYZ(
    array: numpy.ndarray,
    source_colorspace: RgbColorspace,
    whitepoint_XYZ: Optional[Whitepoint] = None,
    chromatic_adaptation_transform: Optional[ChromaticAdaptationTransform] = None,
) -> numpy.ndarray:
    """
    Convert given *RGB* colourspace array to *CIE XYZ* tristimulus values.
    """
    # TODO remove source_colorspace.gamut and test
    if source_colorspace.is_no_op or source_colorspace.gamut is None:
        return array.copy()

    RGB = colour.utilities.to_domain_1(array)

    if (
        source_colorspace.transfer_functions is not None
        and source_colorspace.transfer_functions.decoding is not None
    ):
        with colour.utilities.domain_range_scale("ignore"):
            RGB = source_colorspace.transfer_functions.decoding(RGB)

    XYZ = colour.algebra.vector_dot(source_colorspace.matrix_to_XYZ, RGB)

    if (
        chromatic_adaptation_transform is not None
        and not source_colorspace.whitepoint
        or whitepoint_XYZ is None
    ):
        raise ValueError(
            f"missing whitepoint on one of the argument: "
            f"source_colorspace {source_colorspace.whitepoint}, "
            f"whitepoint_XYZ {whitepoint_XYZ}"
        )

    if chromatic_adaptation_transform is not None:
        M_CAT = matrix_chromatic_adaptation_transform(
            source_colorspace.whitepoint,
            whitepoint_XYZ,
            chromatic_adaptation_transform,
        )
        XYZ = colour.algebra.vector_dot(M_CAT, XYZ)

    return colour.utilities.from_range_1(XYZ)


def XYZ_to_colorspace(
    array: numpy.ndarray,
    target_colorspace: RgbColorspace,
    whitepoint_XYZ: Optional[Whitepoint] = None,
    chromatic_adaptation_transform: Optional[ChromaticAdaptationTransform] = None,
) -> numpy.ndarray:
    """
    Convert given *CIE XYZ* tristimulus values to given *RGB* colourspace.
    """
    # TODO remove target_colorspace.gamut and test
    if target_colorspace.is_no_op or target_colorspace.gamut is None:
        return array.copy()

    XYZ = array

    if (
        chromatic_adaptation_transform is not None
        and not target_colorspace.whitepoint
        or whitepoint_XYZ is None
    ):
        raise ValueError(
            f"missing whitepoint on one of the argument: "
            f"target_colorspace {target_colorspace.whitepoint}, "
            f"whitepoint_XYZ {whitepoint_XYZ}"
        )

    if chromatic_adaptation_transform is not None:
        M_CAT = matrix_chromatic_adaptation_transform(
            whitepoint_XYZ,
            target_colorspace.whitepoint,
            chromatic_adaptation_transform,
        )
        XYZ = colour.algebra.vector_dot(M_CAT, XYZ)

    RGB = colour.algebra.vector_dot(target_colorspace.matrix_from_XYZ, XYZ)

    if (
        target_colorspace.transfer_functions is not None
        and target_colorspace.transfer_functions.encoding is not None
    ):
        with colour.utilities.domain_range_scale("ignore"):
            RGB = target_colorspace.transfer_functions.encoding(RGB)

    return RGB


def colorspace_to_colorspace(
    array: numpy.ndarray,
    source_colorspace: RgbColorspace,
    target_colorspace: RgbColorspace,
    chromatic_adaptation_transform: Optional[ChromaticAdaptationTransform] = None,
):
    """
    Convert given *array* colourspace array from given input *RGB* colourspace
    to output *RGB* colourspace using given *chromatic adaptation* method.

    Note:
        shameless copy of colour.RGB_to_RGB()

    Args:
        array:
        source_colorspace:
        target_colorspace:
        chromatic_adaptation_transform: for whitepoint conversion

    Returns:
        array converted to the given colorspace
    """
    if source_colorspace.is_no_op or target_colorspace.is_no_op:
        return array.copy()
    if source_colorspace == target_colorspace:
        return array.copy()

    RGB = colour.utilities.to_domain_1(array)

    if (
        source_colorspace.transfer_functions is not None
        and source_colorspace.transfer_functions.decoding is not None
    ):
        with colour.utilities.domain_range_scale("ignore"):
            RGB = source_colorspace.transfer_functions.decoding(RGB)

    matrix = matrix_colorspace_to_colorspace(
        source_colorspace,
        target_colorspace,
        chromatic_adaptation_transform,
    )

    RGB = colour.algebra.vector_dot(matrix, RGB)

    if (
        target_colorspace.transfer_functions is not None
        and target_colorspace.transfer_functions.encoding is not None
    ):
        with colour.utilities.domain_range_scale("ignore"):
            RGB = target_colorspace.transfer_functions.encoding(RGB)

    return colour.utilities.from_range_1(RGB)
