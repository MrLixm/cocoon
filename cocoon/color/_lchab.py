from __future__ import annotations

__all__ = (
    "LCHabColor",
    "generate_chroma_gradient",
    "generate_hab_gradient",
    "generate_lightness_gradient",
)

import dataclasses
import logging
from typing import Any
from typing import Generator
from typing import Literal
from typing import overload
from typing import Optional
from typing import Union

import colour
import numpy

from ._rgb import RGBAColor
from ._xyz import XYZColor
from cocoon import RgbColorspace
from cocoon import ChromaticAdaptationTransform

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class LCHabColor:
    """
    Dataclass to represent a color expressed under the LCHab color model.

    Internal values are stored as floats.

    Args:
        lightness: [0-100] range, human relative
        chroma: [0-100] range, relative saturation
        hue: [0-360] range, hue angle
        alpha: optional alpha values associated with the LCHab triplet. [0-1] range.

    References:
        - [1] https://en.wikipedia.org/wiki/CIELAB_color_space#CIEHLC_cylindrical_model
    """

    lightness: float
    chroma: float
    hue: float
    alpha: Optional[float] = None

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}<(L={self.L}, C={self.C}, Hab={self.Hab}, {self.a})"
            f"at {hex(id(self))}>"
        )

    @property
    def Hab(self) -> float:
        return self.hue

    @property
    def C(self) -> float:
        return self.chroma

    @property
    def L(self) -> float:
        return self.lightness

    @property
    def a(self) -> Optional[float]:
        return self.alpha

    @classmethod
    def from_array(
        cls,
        array: numpy.ndarray,
        alpha: Optional[float] = None,
    ) -> LCHabColor:
        """

        Args:
            array:
                L,C,Hab triplet with an optional 4th alpha component.
                [L,C,Hab] or [L,C,Hab,a].
                LCHab channels are expressed in floats.
            alpha: optional alpha values associated with the LCHab triplet. [0-1] range.

        Returns:
            LCHabColor instance corresponding to the given parameters.
        """

        if array.shape[0] == 4 and alpha is None:
            alpha = array[3]

        return cls(array[0], array[1], array[2], alpha=alpha)

    @classmethod
    def from_Rgba(cls, rgba: RGBAColor) -> LCHabColor:
        """
        Note: no chromatic adaptation is performed.

        Args:
            rgba: RGB color to convert

        Returns:
            LCHabColor instance
        """
        xyz = XYZColor.from_Rgba(
            rgba,
            source_colorspace=rgba.colorspace,
            whitepoint_XYZ=rgba.colorspace.whitepoint,
        )
        xyz_array = xyz.to_array(alpha=False)
        lab_array = colour.XYZ_to_Lab(xyz_array, xyz.whitepoint.coordinates)
        lchab_array = colour.Lab_to_LCHab(lab_array)
        return cls.from_array(lchab_array, alpha=rgba.alpha)

    def copy(self) -> LCHabColor:
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
            array(3,) == [L,C,Hab] or array(4,) == [ L,C,Hab,a]
        """
        return numpy.array(self.to_float(alpha=alpha), dtype=numpy.core.float32)

    def to_Rgba(
        self,
        colorspace: RgbColorspace,
        cat: Union[ChromaticAdaptationTransform, bool] = True,
    ) -> RGBAColor:
        """

        Args:
            colorspace: target colorspace for the RGB color. MUST have a whitepoint.
            cat:
                chromatic adaptation transform to use.
                True to use default. False to not use any.

        Returns:
            RGB color instance.
        """
        lchab_array = self.to_array(alpha=False)
        lab_array = colour.LCHab_to_Lab(lchab_array)
        xyz_array = colour.Lab_to_XYZ(
            lab_array,
            illuminant=colorspace.whitepoint.coordinates,
        )
        xyz = XYZColor.from_array(
            xyz_array,
            whitepoint=colorspace.whitepoint,
            alpha=self.alpha,
        )
        return xyz.to_Rgba(colorspace=colorspace, cat=cat)

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
            (L,C,Hab) or (L,C,Hab,a) where components are floats
        """
        if alpha is False:
            return self.L, self.C, self.Hab

        if alpha is True and self.alpha is not None:
            return self.L, self.C, self.Hab, self.alpha

        return self.L, self.C, self.Hab, alpha


def _generate_gradient(
    samples: int,
    hab: Optional[float] = 0,
    lightness: Optional[float] = 90,
    chroma: Optional[float] = 90,
) -> Generator[LCHabColor, Any, Any]:
    """
    Generate a gradient for the channel parameter out of the 3 that is None.

    The gradient cover the whole range of the channel.

    Only one of hab, lightness, chroma, can be None at a time.

    Args:
        samples: number of "points" that define the gradient.
        hab: [0-360] range
        lightness: [0-100] range
        chroma: [0-100] range

    Returns:
        list of gradient "points" as LCHabColor instance
    """

    if hab is None:
        domain = [0, 360]
    else:
        domain = [0, 100]

    array = numpy.linspace(*domain, samples, dtype=numpy.core.int16)

    for component_value in array:
        if hab is None:
            lchab = LCHabColor(lightness=lightness, chroma=chroma, hue=component_value)

        elif lightness is None:
            lchab = LCHabColor(lightness=component_value, chroma=chroma, hue=hab)

        elif chroma is None:
            lchab = LCHabColor(lightness=lightness, chroma=component_value, hue=hab)

        else:
            raise ValueError(
                f"Only on component can be None out of {hab=}, {chroma=}, {lightness=}"
            )

        yield lchab


def generate_hab_gradient(
    samples: int,
    lightness: Optional[float] = 90,
    chroma: Optional[float] = 90,
) -> Generator[LCHabColor, Any, Any]:
    """
    Generate a gradient that cover the full Hab range.

    Args:
        samples: number of point on the gradient
        lightness:
        chroma:

    Returns:
        Generator of ordered LCHabColor each representing a gradient point.
    """
    return _generate_gradient(
        samples=samples,
        hab=None,
        lightness=lightness,
        chroma=chroma,
    )


def generate_chroma_gradient(
    samples: int,
    hab: Optional[float] = 0,
    lightness: Optional[float] = 90,
) -> Generator[LCHabColor, Any, Any]:
    """
    Generate a gradient that cover the full Chroma range.

    Args:
        samples: number of point on the gradient
        hab:
        lightness:

    Returns:
        Generator of ordered LCHabColor each representing a gradient point.
    """
    return _generate_gradient(
        samples=samples,
        hab=hab,
        lightness=lightness,
        chroma=None,
    )


def generate_lightness_gradient(
    samples: int,
    hab: Optional[float] = 0,
    chroma: Optional[float] = 90,
) -> Generator[LCHabColor, Any, Any]:
    """
    Generate a gradient that cover the full Lightness range.

    Args:
        samples: number of point on the gradient
        hab:
        chroma:

    Returns:
        Generator of ordered LCHabColor each representing a gradient point.
    """
    return _generate_gradient(
        samples=samples,
        hab=hab,
        lightness=None,
        chroma=chroma,
    )
