__all__ = (
    "convert_int8_to_float",
    "convert_float_to_int8",
)

import logging

import numpy

logger = logging.getLogger(__name__)


def convert_int8_to_float(source: numpy.ndarray):
    """
    Convert a 8bit RGB color to floating point encoding.

    Result is clamped in the [0-1] range.

    Args:
        source: arbitrary length array of integers

    Returns:
        new array of the same length as float encoding
    """
    intermediate = numpy.clip(source, 0, 255)
    return intermediate.astype(numpy.core.float32) / 255


def convert_float_to_int8(source: numpy.ndarray):
    """
    Convert a floating point array of color values to 8bit integer encoding.

    Result is clamped in the [0-255] range.

    Args:
        source: arbitrary length array of floats

    Returns:
       new  array of the same length as 8bit encoding
    """
    intermediate = numpy.clip(source, 0, 1)
    intermediate *= 255
    intermediate += 0.5
    return intermediate.astype(numpy.uint8)
