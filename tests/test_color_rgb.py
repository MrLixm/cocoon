import numpy
from numpy.testing import assert_allclose
from numpy.testing import assert_array_equal

from cocoon.colorspaces import sRGB_COLORSPACE
from cocoon.color import RGBAColor


COLOR_DATASET = {
    0: {
        "float": (0.5, 0.2, 0.3),
        "8bit": (128, 51, 77),
        "floatFrom8": (0.5, 0.2, 0.3),
        "hex": "#80334D",
    },
    1: {
        "float": (1, 0.3, 0.3),
        "8bit": (255, 77, 77),
        "floatFrom8": (1, 0.3, 0.3),
        "hex": "#FF4D4D",
    },
    2: {
        "float": (0.766, -0.1, 0.15),
        "8bit": (195, 0, 38),
        "floatFrom8": (0.766, 0, 0.15),
        "hex": "#C30026",
    },
    3: {
        "float": (2, -0.333, 0),
        "8bit": (255, 0, 0),
        "floatFrom8": (1, 0, 0),
        "hex": "#FF0000",
    },
    4: {
        "float": (0.005, 0.456, 0.9999),
        "8bit": (1, 116, 255),
        "floatFrom8": (0.005, 0.456, 0.9999),
        "hex": "#0174FF",
    },
}


def test_RGBAColor_init():
    # none should raise error
    color = RGBAColor(0.1, 0.5, 0.2, sRGB_COLORSPACE, 0.6)
    color = RGBAColor(-0.1, 0.5, 1.2, sRGB_COLORSPACE, -0.5)
    color = RGBAColor(-0.1, 0.5, 1.2, sRGB_COLORSPACE, None)
    color = RGBAColor(*(-0.1, 0.5, 1.2), sRGB_COLORSPACE, None)
    color = RGBAColor(-0.1, 0.5, 1.2, "this is possible")
    color = RGBAColor(-0.1, 0.5, 1.2, None, None)


def test_RGBAColor_prop():
    colorValue = (0.12, 1.896, 0.3)

    color = RGBAColor(*colorValue, sRGB_COLORSPACE)

    assert colorValue[0] == color.red
    assert colorValue[0] == color.r
    assert colorValue[1] == color.green
    assert colorValue[1] == color.g
    assert colorValue[2] == color.blue
    assert colorValue[2] == color.b
    assert None is color.alpha
    assert None is color.a

    colorValue = COLOR_DATASET[3]["float"]

    color = RGBAColor(*colorValue, sRGB_COLORSPACE, 0.33)

    assert colorValue[0] == color.red
    assert colorValue[0] == color.r
    assert colorValue[1] == color.green
    assert colorValue[1] == color.g
    assert colorValue[2] == color.blue
    assert colorValue[2] == color.b
    assert 0.33 == color.alpha
    assert 0.33 == color.a


def test_RGBAColor_classMethod_8bit():
    tolerance = 0.002

    for color_dataset in COLOR_DATASET.values():
        color_8bit = color_dataset["8bit"]
        expected = color_dataset["floatFrom8"]

        color = RGBAColor.from_int8(*color_8bit, alpha=None)
        assert_allclose(expected[0], color.red, atol=tolerance)
        assert_allclose(expected[0], color.r, atol=tolerance)
        assert_allclose(expected[1], color.green, atol=tolerance)
        assert_allclose(expected[1], color.g, atol=tolerance)
        assert_allclose(expected[2], color.blue, atol=tolerance)
        assert_allclose(expected[2], color.b, atol=tolerance)
        assert None is color.alpha
        assert None is color.a


def test_RGBAColor_classMethod_hex():
    tolerance = 0.002

    for color_dataset in COLOR_DATASET.values():
        color_floatFrom8 = color_dataset["floatFrom8"]
        color_hex = color_dataset["hex"]

        color = RGBAColor.from_hex(color_hex, alpha=0.33)
        assert_allclose(color_floatFrom8[0], color.red, atol=tolerance)
        assert_allclose(color_floatFrom8[0], color.r, atol=tolerance)
        assert_allclose(color_floatFrom8[1], color.green, atol=tolerance)
        assert_allclose(color_floatFrom8[1], color.g, atol=tolerance)
        assert_allclose(color_floatFrom8[2], color.blue, atol=tolerance)
        assert_allclose(color_floatFrom8[2], color.b, atol=tolerance)
        assert 0.33 is color.alpha
        assert 0.33 is color.a


def test_RGBAColor_classMethod_array():
    array = numpy.array(COLOR_DATASET[3]["float"])
    color = RGBAColor.from_array(array, sRGB_COLORSPACE)
    assert array[0] == color.red
    assert array[0] == color.r
    assert array[1] == color.green
    assert array[1] == color.g
    assert array[2] == color.blue
    assert array[2] == color.b
    assert None == color.alpha
    assert None == color.a

    array = numpy.array(COLOR_DATASET[3]["float"])
    array = numpy.append(array, 0.2)
    color = RGBAColor.from_array(array, sRGB_COLORSPACE)
    assert array[0] == color.red
    assert array[0] == color.r
    assert array[1] == color.green
    assert array[1] == color.g
    assert array[2] == color.blue
    assert array[2] == color.b
    assert 0.2 == color.alpha
    assert 0.2 == color.a


def test_RGBAColor_to_array():
    array = numpy.array(COLOR_DATASET[3]["float"], dtype=numpy.float32)
    color = RGBAColor.from_array(array, sRGB_COLORSPACE)
    result = color.to_array(alpha=False)
    assert_array_equal(result, array)

    array = numpy.array(COLOR_DATASET[3]["float"])
    expected = numpy.append(array, 0.36).astype(numpy.float32)
    color = RGBAColor.from_array(array, sRGB_COLORSPACE)
    result = color.to_array(alpha=0.36)
    assert_array_equal(result, expected)

    array = numpy.array(COLOR_DATASET[3]["float"], dtype=numpy.float32)
    array = numpy.append(array, 0.2).astype(numpy.float32)
    color = RGBAColor.from_array(array, sRGB_COLORSPACE)
    result = color.to_array()
    assert_array_equal(result, array)


def test_RGBAColor_to_tuple():
    for color_dataset in COLOR_DATASET.values():
        color_float = color_dataset["float"]
        expected = (*color_float, 0.44)

        color = RGBAColor(*color_float, sRGB_COLORSPACE, 0.44)
        assert color.to_float() == expected


def test_RGBAColor_to_hex():
    for index, dataset in COLOR_DATASET.items():
        source = dataset["float"]
        expected = dataset["hex"].lower()

        color = RGBAColor(*source, sRGB_COLORSPACE, 0.44)
        result = color.to_hex()
        assert result == expected


def test_RGBAColor_to_int8():
    for index, dataset in COLOR_DATASET.items():
        source = dataset["float"]
        expected = dataset["8bit"]

        color = RGBAColor(*source, sRGB_COLORSPACE, 0.44)
        result = color.to_int8(alpha=False)
        assert result == expected
        expected = (*expected, 0.44)
        result = color.to_int8(alpha=True)
        assert result == expected


def test_RGBAColor_eq():
    colorA = RGBAColor(0.356, 0.12, -0.1, sRGB_COLORSPACE, 0.33)
    colorB = RGBAColor(0.356, 0.12, -0.1, sRGB_COLORSPACE, None)
    colorC = RGBAColor(0.356, 0.12, -0.1, sRGB_COLORSPACE, 0.33)
    colorD = RGBAColor(0.356, 0.12, -0.1, None, 0.33)
    colorE = RGBAColor(0.356001, 0.12, -0.1, sRGB_COLORSPACE, 0.33)

    assert colorA == colorC
    assert colorA != colorE
    assert colorA != colorB
    assert colorA != colorD
    assert colorB != colorD


def test_RGBAColor_copy():
    for index, dataset in COLOR_DATASET.items():
        source = dataset["float"]
        color = RGBAColor(*source, sRGB_COLORSPACE, 0.44)
        color_copy = color.copy()
        assert color == color_copy
        assert color is not color_copy
