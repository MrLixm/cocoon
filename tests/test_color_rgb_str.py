import pytest

from cocoon import sRGB_COLORSPACE
from cocoon.color import RGBAColor
from cocoon.color import ColorStringFormat
from cocoon.color import ValidatorResult
from cocoon.color import convert_str_to_color
from cocoon.color import convert_color_to_str
from cocoon.color import fix_color_str
from cocoon.color import validate_color_str


def test_convert_str_to_color():
    source = "-0.3000 1.6230 0.0005"
    expected = RGBAColor(-0.3, 1.623, 0.0005, colorspace=None, alpha=None)
    result = convert_str_to_color(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "-0.3000 1.6230 0.000567"
    expected = RGBAColor(-0.3, 1.623, 0.000567, colorspace=None, alpha=None)
    result = convert_str_to_color(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "(-0.3000, 1.6230, 0.0005)"
    expected = RGBAColor(-0.3, 1.623, 0.0005, colorspace=None, alpha=None)
    result = convert_str_to_color(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0 255 0"
    expected = RGBAColor(0.0, 1.0, 0.0, colorspace=None, alpha=None)
    result = convert_str_to_color(source, ColorStringFormat.uint8)
    assert result == expected

    source = "0 511 0"
    expected = RGBAColor(0.0, 1.0, 0.0, colorspace=None, alpha=None)
    result = convert_str_to_color(source, ColorStringFormat.uint8)
    assert result == expected

    source = "#00ff00"
    expected = RGBAColor(0.0, 1.0, 0.0, colorspace=sRGB_COLORSPACE, alpha=None)
    result = convert_str_to_color(source, ColorStringFormat.hex)
    assert result == expected


def test_convert_color_to_str():
    source = RGBAColor(-0.3, 1.623, 0.0005, colorspace=None, alpha=None)
    expected = "-0.3000 1.6230 0.0005"
    result = convert_color_to_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = RGBAColor(-0.3, 1.623, 0.0005658, colorspace=None, alpha=None)
    expected = "-0.3000 1.6230 0.0006"
    result = convert_color_to_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = RGBAColor(-0.3, 1.623, 0.0005, colorspace=None, alpha=None)
    expected = "(-0.3000, 1.6230, 0.0005)"
    result = convert_color_to_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = RGBAColor(-0.3, 1.623, 0.0005, colorspace=None, alpha=None)
    expected = "0 255 0"
    result = convert_color_to_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = RGBAColor(0.0, 1.0, 0.0, colorspace=None, alpha=None)
    expected = "0 255 0"
    result = convert_color_to_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = RGBAColor(0.0, 1.0, 0.0, colorspace=sRGB_COLORSPACE, alpha=None)
    expected = "#00ff00"
    result = convert_color_to_str(source, ColorStringFormat.hex)
    assert result == expected

    source = RGBAColor(0.0, 1.0, 0.0, colorspace=None, alpha=None)
    expected = "#00ff00"
    result = convert_color_to_str(source, ColorStringFormat.hex)
    assert result == expected

    source = RGBAColor(-0.3, 1.623, 0.0005, colorspace=None, alpha=0.5)
    expected = "-0.3000 1.6230 0.0005"
    result = convert_color_to_str(source, ColorStringFormat.float_d4)
    assert result == expected


def test_fix_color_str__float_d4():
    source = "0.0"
    expected = "0.0000 0.0000 0.0000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.0 0.0"
    expected = "0.0000 0.0000 0.0000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.15 0.3"
    expected = "0.1500 0.3000 0.0000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.15"
    expected = "0.1500 0.1500 0.1500"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "-0.15"
    expected = "-0.1500 -0.1500 -0.1500"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "1 2 3"
    expected = "1.0000 2.0000 3.0000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "1.0  2.0   3.0"
    expected = "1.0000 2.0000 3.0000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = " 1  2   3"
    expected = "1.0000 2.0000 3.0000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "1  -2   3 "
    expected = "1.0000 -2.0000 3.0000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "-.5 -2  -0.1"
    expected = "-0.5000 -2.0000 -0.1000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "-.5 ---2  -0.1"
    expected = "-0.5000 -2.0000 -0.1000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.15 0.3.5"
    expected = "0.1500 0.3500 0.0000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.15 0..5"
    expected = "0.1500 0.5000 0.0000"
    result = fix_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "(0.15 0.35)"
    with pytest.raises(ValueError):
        fix_color_str(source, ColorStringFormat.float_d4)


def test_validate_color_str__float_d4():
    source = "0.0 0.0 0.0"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.0000 0.0000 0.0000"
    expected = ValidatorResult.valid
    result = validate_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "-0.0000 0.5000 -0.3000"
    expected = ValidatorResult.valid
    result = validate_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.0500"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.0500 0..3"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.3 0.9 001"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4)
    assert result == expected

    source = "0.3 0.9 0,1"
    expected = ValidatorResult.invalid
    result = validate_color_str(source, ColorStringFormat.float_d4)
    assert result == expected


def test_fix_color_str__float_d4_tuple():
    source = "(-1.6, 1.3000, 0.2222)"
    expected = "(-1.6000, 1.3000, 0.2222)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(-1.6, 1.3000, 0.2222"
    expected = "(-1.6000, 1.3000, 0.2222)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.0"
    expected = "(0.0000, 0.0000, 0.0000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(0.0)"
    expected = "(0.0000, 0.0000, 0.0000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(0.0 0.0)"
    expected = "(0.0000, 0.0000, 0.0000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.15 0.3"
    expected = "(0.1503, 0.1503, 0.1503)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.15,0.3"
    expected = "(0.1500, 0.3000, 0.0000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(-0.15)"
    expected = "(-0.1500, -0.1500, -0.1500)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(-0.15,)"
    expected = "(-0.1500, -0.1500, -0.1500)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(-0.15,"
    expected = "(-0.1500, -0.1500, -0.1500)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "1,2 3"
    expected = "(1.0000, 23.0000, 0.0000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(1.0,  2.0,   3.0)"
    expected = "(1.0000, 2.0000, 3.0000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "( 1,  2,,   3)"
    expected = "(1.0000, 2.0000, 3.0000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "1,-2  , 3 )"
    expected = "(1.0000, -2.0000, 3.0000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(-.5, -2,  -0.1)"
    expected = "(-0.5000, -2.0000, -0.1000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "-.5, ---2,  -0.1"
    expected = "(-0.5000, -2.0000, -0.1000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.15, 0..5"
    expected = "(0.1500, 0.5000, 0.0000)"
    result = fix_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected


def test_validate_color_str__float_d4_tuple():
    source = "-.5, --,-2,  -0.1"
    expected = ValidatorResult.invalid
    result = validate_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.0 0.0 0.0"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.0000 0.0000 0.0000"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(0.0000 0.0000 0.0000)"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "(-0.0000, 0.5000, -0.3000)"
    expected = ValidatorResult.valid
    result = validate_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.0500"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.0500 0..3"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.3, 0.9, 001"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected

    source = "0.3, 0.9, 0,1"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.float_d4_tuple)
    assert result == expected


def test_fix_color_str__uint8():
    source = "00 0  0"
    expected = "0 0 0"
    result = fix_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "26 150"
    expected = "26 150 0"
    result = fix_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "26 "
    expected = "26 26 26"
    result = fix_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "13 150 255"
    expected = "13 150 255"
    result = fix_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "  13 150 255  "
    expected = "13 150 255"
    result = fix_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "13 150 255 250"
    expected = "13 150 255"
    result = fix_color_str(source, ColorStringFormat.uint8)
    assert result == expected


def test_validate_color_str__uint8():
    source = "255 255 255"
    expected = ValidatorResult.valid
    result = validate_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "350 125 654"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "230 125 -6"
    expected = ValidatorResult.invalid
    result = validate_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "1"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "a"
    expected = ValidatorResult.invalid
    result = validate_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "1 1 1"
    expected = ValidatorResult.valid
    result = validate_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "00 0 0"
    expected = ValidatorResult.valid  # TODO turn into acceptable ?
    result = validate_color_str(source, ColorStringFormat.uint8)
    assert result == expected

    source = "26 150 "
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.uint8)
    assert result == expected


def test_fix_color_str__hex():
    source = "##fefefe"
    expected = "#fefefe"
    result = fix_color_str(source, ColorStringFormat.hex)
    assert result == expected

    source = "#fe"
    expected = "#fefefe"
    result = fix_color_str(source, ColorStringFormat.hex)
    assert result == expected

    source = "#5"
    expected = "#500000"
    result = fix_color_str(source, ColorStringFormat.hex)
    assert result == expected


def test_validate_color_str__hex():
    source = "fefefe"
    expected = ValidatorResult.invalid
    result = validate_color_str(source, ColorStringFormat.hex)
    assert result == expected

    source = "#fe"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.hex)
    assert result == expected

    source = "#d5fez6"
    expected = ValidatorResult.invalid
    result = validate_color_str(source, ColorStringFormat.hex)
    assert result == expected

    source = "#fefefe"
    expected = ValidatorResult.valid
    result = validate_color_str(source, ColorStringFormat.hex)
    assert result == expected

    source = "#fe fefe"
    expected = ValidatorResult.invalid
    result = validate_color_str(source, ColorStringFormat.hex)
    assert result == expected

    source = "#feFEfe"
    expected = ValidatorResult.valid
    result = validate_color_str(source, ColorStringFormat.hex)
    assert result == expected

    source = "##fefefe"
    expected = ValidatorResult.acceptable
    result = validate_color_str(source, ColorStringFormat.hex)
    assert result == expected
