import numpy
import pytest
from numpy.testing import assert_almost_equal

from cocoon.colorspaces import get_colorspace
from cocoon.color import LCHabColor
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


def test_LCHabColor_init():
    # none should raise error
    LCHabColor(0.2, -0.1, 180, 0.6)
    LCHabColor(10.2, 55.3, 360, -0.5)
    LCHabColor(100, 26.2, -5.2, None)
    LCHabColor(*(-0.1, 0.5, 1.2), None)
    LCHabColor(25.3, 0.5, 50.444)


def test_LCHabColor_prop():
    color = LCHabColor(80, 60, 30.2)
    assert color.lightness == 80
    assert color.L == 80
    assert color.chroma == 60
    assert color.C == 60
    assert color.Hab == 30.2
    assert color.hue == 30.2


def test_LCHabColor_from_to_RGBA():
    rgba_color = RGBAColor(0.3, 0.5, 0.6)
    # no colorspace so raise
    with pytest.raises(AttributeError):
        lchab_color = LCHabColor.from_Rgba(rgba_color)

    rgba_color = RGBAColor(0.3, 0.5, 0.6, COLORSPACE_A, 0.3)
    lchab_color = LCHabColor.from_Rgba(rgba_color)
    new_rgba_color = lchab_color.to_Rgba(COLORSPACE_A, cat=True)

    assert new_rgba_color.colorspace == rgba_color.colorspace
    assert new_rgba_color.alpha == rgba_color.alpha
    assert_almost_equal(new_rgba_color.red, rgba_color.red)
    assert_almost_equal(new_rgba_color.green, rgba_color.green)
    assert_almost_equal(new_rgba_color.blue, rgba_color.blue)
