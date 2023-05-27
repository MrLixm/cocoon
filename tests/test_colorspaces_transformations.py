import numpy
import pytest
from numpy.testing import assert_array_equal

import colour
from cocoon import colorspaces


class Sources:
    def __init__(self):
        whitepoint_coord = colour.colorimetry.CCS_ILLUMINANTS[
            "CIE 1931 2 Degree Standard Observer"
        ]["D65"]
        self.whitepoint_D65 = colorspaces.Whitepoint(
            "D65", coordinates=whitepoint_coord
        )

        whitepoint_coord = colour.colorimetry.CCS_ILLUMINANTS[
            "CIE 1931 2 Degree Standard Observer"
        ]["D55"]
        self.whitepoint_D55 = colorspaces.Whitepoint(
            "D55", coordinates=whitepoint_coord
        )

        self.colorspaces_acescg = colorspaces.get_colorspace("ACEScg")
        self.colorspace_srgb = colorspaces.get_colorspace("ACES2065-1")
        self.colorspace_raw = colorspaces.get_colorspace("raw")


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


def test_matrix_chromatic_adaptation_transform():
    sources = Sources()

    # SOURCE: http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
    expected = numpy.array(
        [
            [1.0285405, 0.0135022, -0.0314825],
            [0.0172109, 0.9952227, -0.0106363],
            [-0.0058993, 0.0096778, 0.8425735],
        ]
    )

    result = colorspaces.matrix_chromatic_adaptation_transform(
        source_whitepoint=sources.whitepoint_D65,
        target_whitepoint=sources.whitepoint_D55,
        transform_name=colorspaces.ChromaticAdaptationTransform.bradford,
    )
    # seems bruce matrices are not that accurate compared to colour ones.
    numpy.testing.assert_allclose(result, expected, rtol=0.001, atol=0.00025)

    result = colorspaces.matrix_chromatic_adaptation_transform(
        source_whitepoint=sources.whitepoint_D65,
        target_whitepoint=sources.whitepoint_D65,
        transform_name=colorspaces.ChromaticAdaptationTransform.bradford,
    )
    # TODO shouldn't they supposed to be identical ?
    assert not numpy.array_equal(result, numpy.identity(3))
    numpy.testing.assert_allclose(result, numpy.identity(3), atol=0.00000001)


def test_matrix_colorspace_to_colorspace():
    sources = Sources()

    # SOURCE: https://www.colour-science.org/apps/
    expected = numpy.array(
        [
            [1.451439316, -0.236510747, -0.214928569],
            [-0.076553773, 1.176229700, -0.099675926],
            [0.008316148, -0.006032450, 0.997716301],
        ]
    )

    result = colorspaces.matrix_colorspace_to_colorspace(
        source_colorspace=sources.colorspace_srgb,
        target_colorspace=sources.colorspaces_acescg,
        chromatic_adaptation_transform=colorspaces.ChromaticAdaptationTransform.bradford,
    )

    numpy.testing.assert_array_almost_equal(result, expected, decimal=9)

    result2 = colorspaces.matrix_colorspace_to_colorspace(
        source_colorspace=sources.colorspace_srgb,
        target_colorspace=sources.colorspaces_acescg,
        chromatic_adaptation_transform=None,
    )
    assert not numpy.array_equal(result, result2)

    result = colorspaces.matrix_colorspace_to_colorspace(
        source_colorspace=sources.colorspaces_acescg,
        target_colorspace=sources.colorspaces_acescg,
        chromatic_adaptation_transform=colorspaces.ChromaticAdaptationTransform.bradford,
    )
    # TODO shouldn't they supposed to be identical ?
    assert not numpy.array_equal(result, numpy.identity(3))
    numpy.testing.assert_allclose(result, numpy.identity(3), atol=0.00000001)

    result = colorspaces.matrix_colorspace_to_colorspace(
        source_colorspace=sources.colorspace_raw,
        target_colorspace=sources.colorspaces_acescg,
        chromatic_adaptation_transform=colorspaces.ChromaticAdaptationTransform.bradford,
    )
    assert numpy.array_equal(result, numpy.identity(3))


def test_colorspace_to_XYZ():
    sources = Sources()

    source_color = numpy.array([0.3333, 1.25, -0.16])
    result = colorspaces.colorspace_to_XYZ(
        source_color,
        sources.colorspaces_acescg,
        sources.whitepoint_D65,
        colorspaces.ChromaticAdaptationTransform.CAT02,
    )
    assert not numpy.array_equal(source_color, result)

    with pytest.raises(ValueError):
        result = colorspaces.colorspace_to_XYZ(
            source_color,
            sources.colorspaces_acescg,
            None,
            colorspaces.ChromaticAdaptationTransform.CAT02,
        )

    colorspace_bugged = sources.colorspaces_acescg.with_whitepoint(None, None, None)

    with pytest.raises(ValueError):
        result = colorspaces.colorspace_to_XYZ(
            source_color,
            colorspace_bugged,
            sources.whitepoint_D65,
            colorspaces.ChromaticAdaptationTransform.CAT02,
        )


def test_XYZ_to_colorspace():
    sources = Sources()

    source_color = numpy.array([0.3333, 1.25, -0.16])
    result = colorspaces.XYZ_to_colorspace(
        source_color,
        sources.colorspaces_acescg,
        sources.whitepoint_D65,
        colorspaces.ChromaticAdaptationTransform.CAT02,
    )
    assert not numpy.array_equal(source_color, result)

    with pytest.raises(ValueError):
        result = colorspaces.XYZ_to_colorspace(
            source_color,
            sources.colorspaces_acescg,
            None,
            colorspaces.ChromaticAdaptationTransform.CAT02,
        )

    colorspace_bugged = sources.colorspaces_acescg.with_whitepoint(None, None, None)

    with pytest.raises(ValueError):
        result = colorspaces.XYZ_to_colorspace(
            source_color,
            colorspace_bugged,
            sources.whitepoint_D65,
            colorspaces.ChromaticAdaptationTransform.CAT02,
        )
