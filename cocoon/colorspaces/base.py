from __future__ import annotations

__all__ = (
    "BaseColorspaceComponent",
    "Whitepoint",
    "ColorspaceGamut",
    "TransferFunctions",
    "TRANSFER_FUNCTIONS_LINEAR",
    "RgbColorspace",
)

import copy
import dataclasses
from abc import abstractmethod
from typing import Callable
from typing import Optional

import numpy
import colour

from cocoon.utils import simplify
from cocoon.utils import numpy_array2string_oneline
from cocoon.colorspaces import ColorspaceCategory


@dataclasses.dataclass
class BaseColorspaceComponent:
    """
    Every colorspace entity or component will be derived from this class.

    Expose 2 attributes :
    - name : a human-readable proper name to identify the object
    - name_simplified: the name but in a more simple syntax for easier typing.
    """

    name: str

    def __post_init__(self):
        self.name_simplified = simplify(self.name)

    @abstractmethod
    def _tuplerepr(self) -> tuple:
        """
        The class represented as a tuple object. Used for hashing.
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Subjective dict representation of the class.
        """
        pass

    def __str__(self):
        return f"{self.__class__.__name__}<{self.name} at {hex(id(self))}>"

    def __hash__(self):
        return hash(self._tuplerepr())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._tuplerepr() == other._tuplerepr()
        return NotImplemented


@dataclasses.dataclass(eq=False)
class Whitepoint(BaseColorspaceComponent):
    coordinates: numpy.ndarray
    """
    CIE xy coordinates as a ndarray(2,)
    """

    _coordinates_repr: str = dataclasses.field(init=False, repr=False, default="")
    """
    Variable used to cache the repr() of the array to avoid expensive computations
    every time the instance need to be hashed (via _tuplerepr)
    """

    def __post_init__(self):
        self._coordinates_repr = repr(self.coordinates)

    def __setattr__(self, key, value):
        if key == "coordinates":
            self._coordinates_repr = repr(value)
        super().__setattr__(key, value)

    def _tuplerepr(self):
        return (
            self.__class__.__name__,
            self.name,
            self._coordinates_repr,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "coordinates": numpy_array2string_oneline(self.coordinates),
        }

    @classmethod
    def from_colour_colorspace(cls, colour_colorspace: colour.RGB_Colourspace):
        return cls(
            colour_colorspace.whitepoint_name,
            colour_colorspace.whitepoint.copy(),
        )


@dataclasses.dataclass(eq=False)
class ColorspaceGamut(BaseColorspaceComponent):
    """
    Gamut/Primaries part of a specific colorspace.
    """

    primaries: numpy.ndarray

    _primaries_repr: str = dataclasses.field(init=False, repr=False, default="")
    """
    Variable used to cache the repr() of the array to avoid expensive computations
    every time the instance need to be hashed (via _tuplerepr)
    """

    def __post_init__(self):
        self._primaries_repr = repr(self.primaries)

    def __setattr__(self, key, value):
        if key == "primaries":
            self._primaries_repr = repr(value)
        super().__setattr__(key, value)

    def _tuplerepr(self):
        return (
            self.__class__.__name__,
            self.name,
            self._primaries_repr,
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "primaries": numpy_array2string_oneline(self.primaries),
        }

    @classmethod
    def from_colour_colorspace(cls, colour_colorspace: colour.RGB_Colourspace):
        return cls(
            "Gamut " + colour_colorspace.name,
            colour_colorspace.primaries,
        )


@dataclasses.dataclass(eq=False)
class TransferFunctions(BaseColorspaceComponent):
    """
    Transfer functions as decoding and encoding.

    A transfer function might or might not be linear and need to be specified if so.
    """

    encoding: Optional[Callable]
    decoding: Optional[Callable]

    is_encoding_linear: bool = False
    is_decoding_linear: bool = False

    def _tuplerepr(self):
        return (
            self.__class__.__name__,
            self.name,
            self.encoding,
            self.decoding,
            self.is_encoding_linear,
            self.is_decoding_linear,
        )

    def __post_init__(self):
        super().__post_init__()

        if self.encoding is None:
            self.is_encoding_linear = True
        if self.decoding is None:
            self.is_decoding_linear = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "is_encoding_linear": self.is_encoding_linear,
            "is_decoding_linear": self.is_decoding_linear,
        }

    @property
    def are_linear(self) -> bool:
        """
        Return True if the encoding and decoding are linear transfer-functions.
        """
        return self.is_encoding_linear and self.is_decoding_linear

    @classmethod
    def from_colour_colorspace(cls, colour_colorspace: colour.RGB_Colourspace):
        return cls(
            name="CCTF " + colour_colorspace.name,
            encoding=colour_colorspace.cctf_encoding,
            decoding=colour_colorspace.cctf_decoding,
            is_encoding_linear=colour_colorspace.cctf_encoding
            == colour.linear_function,
            is_decoding_linear=colour_colorspace.cctf_decoding
            == colour.linear_function,
        )


TRANSFER_FUNCTIONS_LINEAR = TransferFunctions("CCTF Linear", None, None)


@dataclasses.dataclass(eq=False)
class RgbColorspace(BaseColorspaceComponent):
    """
    Top level entity specifying how a colorspace is defined.

    By color-science standard, every colorspace define :
    - gamut
    - whitepoint
    - transfer functions

    To perform colorspace conversion a 3x3 matrix from and to CIE XYZ is required,
    which can be derived automatically from the gamut and whitepoint if not specified.

    """

    gamut: Optional[ColorspaceGamut]
    whitepoint: Optional[Whitepoint]
    transfer_functions: Optional[TransferFunctions]

    categories: list[ColorspaceCategory]
    """
    To help sort the colorspace in an interface.
    """

    description: str
    """
    A bit more details on what/why for this colorspace.
    """

    matrix_to_XYZ: numpy.ndarray = None
    matrix_from_XYZ: numpy.ndarray = None

    _linear_source: Optional[RgbColorspace] = None
    """
    Initial colorspace this instance was derived from when linearized.
    """

    def __post_init__(self):
        super().__post_init__()
        # need a tuple to be hashable
        self.categories: tuple[ColorspaceCategory] = tuple(self.categories)

        if (
            self.matrix_to_XYZ is None
            and self.matrix_from_XYZ is None
            and self.gamut
            and self.whitepoint
        ):
            self.matrix_to_XYZ: numpy.ndarray = colour.normalised_primary_matrix(
                primaries=self.gamut.primaries,
                whitepoint=self.whitepoint.coordinates,
            )
            self.matrix_from_XYZ: numpy.ndarray = numpy.linalg.inv(self.matrix_to_XYZ)

    def _tuplerepr(self) -> tuple:
        return (
            self.__class__.__name__,
            self.name,
            self.gamut,
            self.whitepoint,
            self.transfer_functions,
            self.categories,
            self.description,
        )

    @property
    def is_no_op(self) -> bool:
        """
        Return True if the colorspace should not be processed because it
        defines no transform for any component.
        """

        has_gamut = (
            self.gamut is not None
            or (
                self.matrix_from_XYZ is not None
                and not numpy.array_equal(self.matrix_from_XYZ, numpy.identity(3))
            )
            or (
                self.matrix_to_XYZ is not None
                and not numpy.array_equal(self.matrix_to_XYZ, numpy.identity(3))
            )
        )

        has_whitepoint = self.whitepoint is not None

        has_transfer_function = self.transfer_functions is not None and (
            self.transfer_functions.decoding or self.transfer_functions.encoding
        )

        return not has_gamut and not has_whitepoint and not has_transfer_function

    @property
    def is_linear_copy(self) -> bool:
        """
        True if this colorspace was generated from :meth:`as_linear_copy`
        """
        return bool(self._linear_source)

    def copy(self) -> RgbColorspace:
        """
        Return a shallow copy of this instance.
        """
        return copy.deepcopy(self)

    def as_linear_copy(self) -> RgbColorspace:
        """
        Return a copy of this colorspace but with all transfer-functions as linear.

        If the transfer functions are already linear, just return a regular copy.
        """
        colorspace = self.copy()

        if not self.transfer_functions or self.transfer_functions.are_linear:
            return colorspace

        colorspace._linear_source = self
        colorspace.name = colorspace.name + " Linear"
        colorspace.transfer_functions = TRANSFER_FUNCTIONS_LINEAR
        return colorspace

    def retrieve_linear_source(self) -> Optional[RgbColorspace]:
        """
        The non-linear colorspace this linear instance was derived from. Else None
        if :meth:`is_linear_copy` is False.
        """
        return self._linear_source

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "gamut": self.gamut.to_dict(),
            "whitepoint": self.whitepoint.to_dict(),
            "transfer_functions": self.transfer_functions.to_dict(),
            "matrices": {
                "toXYZ": numpy_array2string_oneline(self.matrix_to_XYZ),
                "fromXYZ": numpy_array2string_oneline(self.matrix_from_XYZ),
            },
        }

    @classmethod
    def from_colour_colorspace(
        cls,
        colour_colorspace: colour.RGB_Colourspace,
        categories: list[ColorspaceCategory],
        description: Optional[str] = None,
    ):
        gamut = ColorspaceGamut.from_colour_colorspace(colour_colorspace)
        whitepoint = Whitepoint.from_colour_colorspace(colour_colorspace)
        transfer_functions = TransferFunctions.from_colour_colorspace(colour_colorspace)

        return cls(
            name=colour_colorspace.name,
            gamut=gamut,
            whitepoint=whitepoint,
            transfer_functions=transfer_functions,
            description=description or colour_colorspace.__doc__,
            categories=categories,
            matrix_from_XYZ=colour_colorspace.matrix_XYZ_to_RGB.copy(),
            matrix_to_XYZ=colour_colorspace.matrix_RGB_to_XYZ.copy(),
        )
