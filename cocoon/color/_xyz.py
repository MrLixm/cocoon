from __future__ import annotations

__all__ = ("XYZColor",)

import dataclasses
import logging
from typing import Literal
from typing import overload
from typing import Optional
from typing import Union

import numpy

from cocoon.color import RGBAColor
from cocoon.colorspaces import RgbColorspace
from cocoon.colorspaces import Whitepoint
from cocoon.colorspaces import ChromaticAdaptationTransform
from cocoon.colorspaces import colorspace_to_XYZ
from cocoon.colorspaces import XYZ_to_colorspace

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class XYZColor:
    """
    Dataclass to represent a color expressed under the CIE XYZ color model.

    Internal values are stored as floats.

    Args:
        X: [-0-1+] range
        Y: [-0-1+] range
        Z: [-0-1+] range
        whitepoint: illuminant
        alpha: optional alpha values associated with the XYZ triplet. [0-1] range.

    References:
        - [1] https://en.wikipedia.org/wiki/CIE_1931_color_space
    """

    X: float
    Y: float
    Z: float
    whitepoint: Optional[Whitepoint]
    alpha: Optional[float] = None

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}<(X={self.X}, Y={self.Y}, Z={self.Z}, {self.a})"
            f":{self.whitepoint} at {hex(id(self))}>"
        )

    @property
    def a(self) -> Optional[float]:
        return self.alpha

    @classmethod
    def from_array(
        cls,
        array: numpy.ndarray,
        whitepoint: Optional[Whitepoint] = None,
        alpha: Optional[float] = None,
    ) -> XYZColor:
        """

        Args:
            array:
                X,Y,Z triplet with an optional 4th alpha component.
                [X,Y,Z] or [X,Y,Z,a].
                XYZ channels are expressed in floats.
            whitepoint: illuminant
            alpha: optional alpha values associated with the XYZ triplet. [0-1] range.

        Returns:
            XYZColor instance corresponding to the given parameters.
        """

        if array.shape[0] == 4 and alpha is None:
            alpha = array[3]

        return cls(array[0], array[1], array[2], whitepoint=whitepoint, alpha=alpha)

    @classmethod
    def from_Rgba(
        cls,
        rgba: RGBAColor,
        source_colorspace: RgbColorspace,
        whitepoint_XYZ: Optional[Whitepoint] = None,
        cat: Union[ChromaticAdaptationTransform, bool] = True,
    ) -> XYZColor:
        """

        Args:
            rgba:
                RGB color value to convert.
            source_colorspace:
                colorspace of the input rgba color.
                As a separate parameter to make sure it's mandatory.
            whitepoint_XYZ:
                target illuminant of the XYZ tuple. None means no
                chromatic adaptation will be performed.
            cat:
                chromatic adaptation transform to use.
                True to use default. False to not use any.
        Returns:
            XYZColor instance
        """
        if cat is True:
            cat = ChromaticAdaptationTransform.get_default()
        elif cat is False:
            cat = None

        array = rgba.to_array(alpha=False)
        converted = colorspace_to_XYZ(
            array,
            source_colorspace=source_colorspace,
            whitepoint_XYZ=whitepoint_XYZ,
            chromatic_adaptation_transform=cat,
        )
        return cls.from_array(
            array=converted,
            whitepoint=whitepoint_XYZ,
            alpha=rgba.alpha,
        )

    def copy(self) -> XYZColor:
        """
        Returns:
            return a new instance copy of this one
        """
        return dataclasses.replace(self)

    def to_array(self, alpha: Union[bool, float] = True) -> numpy.ndarray:
        """
        Args:
            alpha:
                - If True, return the internal alpha value if not none at the end of the array. (size 4 or 3)
                - If False, always return a ndarray of size 3
                - If a float, return an array with the value passed (size 4)

        Returns:
            array(3,) == [X,Y,Z] or array(4,) == [X,Y,Z,a]
        """
        return numpy.array(self.to_float(alpha=alpha), dtype=numpy.core.float32)

    def to_Rgba(
        self,
        colorspace: RgbColorspace,
        cat: Union[ChromaticAdaptationTransform, bool] = True,
    ) -> RGBAColor:
        """

        Args:
            colorspace: target colorspace of the RGB color.
            cat:
                 chromatic adaptation transform to use.
                 True to use default. False to not use any.

        Returns:
            RGBA color in the given colorspace
        """
        if cat is True:
            cat = ChromaticAdaptationTransform.get_default()
        elif cat is False:
            cat = None

        array = self.to_array(alpha=False)
        rgba = XYZ_to_colorspace(
            array,
            target_colorspace=colorspace,
            whitepoint_XYZ=self.whitepoint,
            chromatic_adaptation_transform=cat,
        )
        return RGBAColor.from_array(rgba, colorspace=colorspace, alpha=self.alpha)

    @overload
    def to_float(self, alpha: float = ...) -> tuple[float, float, float, float]:
        ...

    @overload
    def to_float(self, alpha: Literal[False] = ...) -> tuple[float, float, float]:
        ...

    @overload
    def to_float(
        self,
        alpha: Literal[True] = ...,
    ) -> Union[tuple[float, float, float], tuple[float, float, float, float]]:
        ...

    def to_float(
        self,
        alpha: Union[bool, float] = True,
    ) -> Union[tuple[float, float, float], tuple[float, float, float, float]]:
        """
        Args:
            alpha:
                - If True, return the internal alpha value if not none at the end of the tuple. (len 4 or 3)
                - If False, always return a tuple of len 3
                - If a float, return a tuple with the value passed (len 4)

        Returns:
            (X,Y,Z) or (X,Y,Z,a) where components are floats
        """
        if alpha is False:
            return self.X, self.Y, self.Z

        if alpha is True and self.alpha is not None:
            return self.X, self.Y, self.Z, self.alpha

        return self.X, self.Y, self.Z, alpha
