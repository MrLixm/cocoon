__all__ = (
    "POINTER_GAMUT_COLORSPACE",
    "sRGB_COLORSPACE",
    "sRGB_LINEAR_COLORSPACE",
    "PASSTHROUGH_COLORSPACE",
)

from cocoon.colorspaces.datasets.browse import get_colorspace
from cocoon.colorspaces.datasets.build import _COLORSPACE_POINTER_GAMUT_NAME


POINTER_GAMUT_COLORSPACE = get_colorspace(_COLORSPACE_POINTER_GAMUT_NAME)
assert POINTER_GAMUT_COLORSPACE

sRGB_COLORSPACE = get_colorspace("sRGB")
assert sRGB_COLORSPACE
sRGB_LINEAR_COLORSPACE = get_colorspace("sRGB", force_linear=True)
assert sRGB_LINEAR_COLORSPACE

PASSTHROUGH_COLORSPACE = get_colorspace("Passthrough")
"""
A 'null' colorspace that does nothing.
"""
assert PASSTHROUGH_COLORSPACE
