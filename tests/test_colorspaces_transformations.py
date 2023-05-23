import numpy
from numpy.testing import assert_array_equal

from cocoon import colorspaces


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
