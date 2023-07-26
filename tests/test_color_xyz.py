import numpy
from numpy.testing import assert_array_equal

from cocoon.colorspaces import get_colorspace
from cocoon.color import XYZColor
from cocoon.color import RGBAColor

COLORSPACE_A = get_colorspace("sRGB")
assert COLORSPACE_A
COLORSPACE_B = get_colorspace("ACES2065-1")
assert COLORSPACE_B
COLORSPACE_C = get_colorspace("DCI-P3")
WHITEPOINT_A = COLORSPACE_A.whitepoint
assert WHITEPOINT_A
WHITEPOINT_B = COLORSPACE_B.whitepoint
assert WHITEPOINT_B


COLOR_DATASET = {
    0: {
        "XYZ": (0.5, 0.2, 0.3),
    },
    1: {
        "XYZ": (1, 0.3, 0.3),
    },
    2: {
        "XYZ": (0.766, -0.1, 0.15),
    },
    3: {
        "XYZ": (2, -0.333, 0),
    },
    4: {
        "XYZ": (0.005, 0.456, 0.9999),
    },
}


def test_XYZColor_init():
    # none should raise error
    XYZColor(0.1, 0.5, 0.2, WHITEPOINT_A, 0.6)
    XYZColor(-0.1, 0.5, 1.2, WHITEPOINT_A, -0.5)
    XYZColor(-0.1, 0.5, 1.2, WHITEPOINT_A, None)
    XYZColor(*(-0.1, 0.5, 1.2), WHITEPOINT_A, None)
    XYZColor(-0.1, 0.5, 1.2, "this is possible")
    XYZColor(-0.1, 0.5, 1.2, None, None)


def test_XYZColor_prop():
    colorValue = (0.12, 1.896, 0.3)

    color = XYZColor(*colorValue, WHITEPOINT_A)

    assert colorValue[0] == color.X
    assert colorValue[1] == color.Y
    assert colorValue[2] == color.Z
    assert None is color.alpha
    assert None is color.a

    colorValue = COLOR_DATASET[3]["XYZ"]

    color = XYZColor(*colorValue, WHITEPOINT_A, 0.33)

    assert colorValue[0] == color.X
    assert colorValue[1] == color.Y
    assert colorValue[2] == color.Z
    assert 0.33 == color.alpha
    assert 0.33 == color.a


def test_XYZColor_classMethod_array():
    array = numpy.array(COLOR_DATASET[3]["XYZ"])
    color = XYZColor.from_array(array, WHITEPOINT_A)
    assert array[0] == color.X
    assert array[1] == color.Y
    assert array[2] == color.Z
    assert None is color.alpha
    assert None is color.a

    array = numpy.array(COLOR_DATASET[3]["XYZ"])
    array = numpy.append(array, 0.2)
    color = XYZColor.from_array(array, WHITEPOINT_A)
    assert array[0] == color.X
    assert array[1] == color.Y
    assert array[2] == color.Z
    assert 0.2 == color.alpha
    assert 0.2 == color.a


def test_XYZColor_to_array():
    array = numpy.array(COLOR_DATASET[3]["XYZ"], dtype=numpy.float32)
    color = XYZColor.from_array(array, WHITEPOINT_A)
    result = color.to_array(alpha=False)
    assert_array_equal(result, array)

    array = numpy.array(COLOR_DATASET[3]["XYZ"])
    expected = numpy.append(array, 0.36).astype(numpy.float32)
    color = XYZColor.from_array(array, WHITEPOINT_A)
    result = color.to_array(alpha=0.36)
    assert_array_equal(result, expected)

    array = numpy.array(COLOR_DATASET[3]["XYZ"], dtype=numpy.float32)
    array = numpy.append(array, 0.2).astype(numpy.float32)
    color = XYZColor.from_array(array, WHITEPOINT_A)
    result = color.to_array()
    assert_array_equal(result, array)


def test_XYZColor_to_tuple():
    for color_dataset in COLOR_DATASET.values():
        color_float = color_dataset["XYZ"]
        expected = (*color_float, 0.44)

        color = XYZColor(*color_float, WHITEPOINT_A, 0.44)
        assert color.to_float() == expected


def test_XYZColor_eq():
    colorA = XYZColor(0.356, 0.12, -0.1, WHITEPOINT_A, 0.33)
    colorB = XYZColor(0.356, 0.12, -0.1, WHITEPOINT_A, None)
    colorC = XYZColor(0.356, 0.12, -0.1, WHITEPOINT_A, 0.33)
    colorD = XYZColor(0.356, 0.12, -0.1, None, 0.33)
    colorE = XYZColor(0.356001, 0.12, -0.1, WHITEPOINT_A, 0.33)

    assert colorA == colorC
    assert colorA != colorE
    assert colorA != colorB
    assert colorA != colorD
    assert colorB != colorD


def test_XYZColor_copy():
    for index, dataset in COLOR_DATASET.items():
        source = dataset["XYZ"]
        color = XYZColor(*source, WHITEPOINT_A, 0.44)
        color_copy = color.copy()
        assert color == color_copy
        assert color is not color_copy


def test_to_Rgba():
    # TODO improve with proper values testing
    colorA = XYZColor(0.356, 0.12, -0.1, WHITEPOINT_A, 0.33)
    rgba = colorA.to_Rgba(COLORSPACE_B)
    assert isinstance(rgba, RGBAColor)
