import numpy
from numpy.testing import assert_array_equal

from cocoon import colorspaces


def test_exr_chromaticities():
    chromat_bt709 = (0.64, 0.33, 0.3, 0.6, 0.15, 0.06, 0.3127, 0.329)
    chromat_CIE_XYZ = (1, 0, 0, 1, 0, 0, 1 / 3, 1 / 3)
    chromat_random = (0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.5, 0.5)
    chromat_apo = (0.7347, 0.2653, 0, 1, 0.0001, -0.077, 0.32168, 0.33767)

    colorspace = colorspaces.get_colorspace("sRGB")
    result = colorspaces.colorspace_to_exr_chromaticities(colorspace)
    assert result == chromat_bt709

    colorspace = colorspaces.get_colorspace("raw")
    result = colorspaces.colorspace_to_exr_chromaticities(colorspace)
    assert result is None

    result = colorspaces.exr_chromaticities_to_colorspace(
        chromat_bt709,
        ensure_linear_cctf=True,
    )
    assert colorspaces.get_colorspace("sRGB").as_linear_copy() in result

    result = colorspaces.exr_chromaticities_to_colorspace(
        chromat_apo,
        ensure_linear_cctf=True,
    )
    assert result == [colorspaces.get_colorspace("ACES2065-1")]

    result = colorspaces.exr_chromaticities_to_colorspace(
        chromat_bt709,
        ensure_linear_cctf=False,
    )
    assert colorspaces.get_colorspace("sRGB") in result
    assert result == [
        colorspaces.get_colorspace("bt709"),
        colorspaces.get_colorspace("sRGB"),
    ]

    result = colorspaces.exr_chromaticities_to_colorspace(
        chromat_CIE_XYZ,
        ensure_linear_cctf=False,
    )
    assert result == []

    result = colorspaces.exr_chromaticities_to_colorspace(
        chromat_random,
        ensure_linear_cctf=False,
    )
    assert result == []

    return


def test_colorspace_to_colorspace_passthrough():
    source = numpy.array([0.3333, 1.25, -0.16])
    expected = source.copy()
    result = colorspaces.colorspace_to_colorspace(
        source,
        source_colorspace=colorspaces.sRGB_COLORSPACE,
        target_colorspace=colorspaces.sRGB_COLORSPACE,
    )
    assert result is not source
    assert_array_equal(result, expected)
