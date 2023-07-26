import numpy
from numpy.testing import assert_allclose
from numpy.testing import assert_array_equal

from cocoon.color import convert_int8_to_float
from cocoon.color import convert_float_to_int8


DATASET = {
    "float_to_uint8": [
        {"source": [0.0, 0.0, 0.0], "expected": [0, 0, 0]},
        {"source": [1.0, 1.0, 1.0], "expected": [255, 255, 255]},
        {"source": [1.1, 0.5, 0.3], "expected": [255, 128, 77]},
        {"source": [-0.322, 0.1, 0.9999], "expected": [0, 26, 255]},
        {"source": [1.0, -1e-06, 0.3333333333333333], "expected": [255, 0, 85]},
    ],
    "uint8_to_float": [
        {"source": [255, 255, 255], "expected": [1.0, 1.0, 1.0]},
        {"source": [0, 0, 0], "expected": [0.0, 0.0, 0.0]},
        {"source": [255, 126, 0], "expected": [1.0, 0.49411768, 0.0]},
        {"source": [0, 1, 0], "expected": [0.0, 0.00392157, 0.0]},
        {"source": [128, 127, 126], "expected": [0.5019608, 0.49803925, 0.49411768]},
    ],
}


def test_convert_float_to_int8():
    for test_data in DATASET["float_to_uint8"]:
        source = numpy.array(test_data["source"], dtype=numpy.float32)
        expected = numpy.array(test_data["expected"], dtype=numpy.uint8)
        result = convert_float_to_int8(source)
        assert_array_equal(result, expected)


def test_convert_int8_to_float():
    for test_data in DATASET["uint8_to_float"]:
        source = numpy.array(test_data["source"], dtype=numpy.uint8)
        expected = numpy.array(test_data["expected"], dtype=numpy.float32)
        result = convert_int8_to_float(source)
        assert_allclose(result, expected, rtol=1e-5)
