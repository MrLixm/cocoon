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
import functools
from abc import abstractmethod
from typing import Callable
from typing import Optional

import numpy
import colour

from cocoon.utils import simplify
from cocoon.utils import numpy_array2string_oneline
from cocoon.colorspaces import ColorspaceCategory


@dataclasses.dataclass(frozen=True)
class BaseColorspaceComponent:
    """
    Every colorspace entity or component will be derived from this class.

    Expose 2 attributes :
    - name : a human-readable proper name to identify the object
    - name_simplified: the name but in a more simple syntax for easier typing.
    """

    name: str

    @functools.cached_property
    def name_simplified(self) -> str:
        """
        the name attribute but in a more simple syntax for easier typing.
        """
        return simplify(self.name)

    @property
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

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<{self.name} at {hex(id(self))}>"

    def __hash__(self) -> int:
        return hash(self._tuplerepr)

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self._tuplerepr == other._tuplerepr
        return False


@dataclasses.dataclass(eq=False, frozen=True)
class Whitepoint(BaseColorspaceComponent):
    coordinates: numpy.ndarray
    """
    CIE xy coordinates as a ndarray(2,)
    """

    @functools.cached_property
    def _tuplerepr(self):
        return (
            self.__class__.__name__,
            self.name,
            repr(self.coordinates),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "coordinates": numpy_array2string_oneline(self.coordinates),
        }

    @classmethod
    def from_colour_colorspace(
        cls, colour_colorspace: colour.RGB_Colourspace
    ) -> Whitepoint:
        return cls(
            colour_colorspace.whitepoint_name,
            colour_colorspace.whitepoint.copy(),
        )


@dataclasses.dataclass(eq=False, frozen=True)
class ColorspaceGamut(BaseColorspaceComponent):
    """
    Gamut/Primaries part of a specific colorspace.
    """

    primaries: numpy.ndarray

    @functools.cached_property
    def _tuplerepr(self):
        return (
            self.__class__.__name__,
            self.name,
            repr(self.primaries),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "primaries": numpy_array2string_oneline(self.primaries),
        }

    @classmethod
    def from_colour_colorspace(
        cls, colour_colorspace: colour.RGB_Colourspace
    ) -> ColorspaceGamut:
        return cls(
            "Gamut " + colour_colorspace.name,
            colour_colorspace.primaries,
        )


@dataclasses.dataclass(eq=False, frozen=True)
class TransferFunctions(BaseColorspaceComponent):
    """
    Transfer functions as decoding and encoding.

    Passing None to one or both of the attribute make them considered linear.
    """

    encoding: Optional[Callable]
    decoding: Optional[Callable]

    @functools.cached_property
    def _tuplerepr(self):
        return (
            self.__class__.__name__,
            self.name,
            self.encoding,
            self.decoding,
            self.is_encoding_linear,
            self.is_decoding_linear,
        )

    @functools.cached_property
    def is_encoding_linear(self) -> bool:
        return self.encoding is None

    @functools.cached_property
    def is_decoding_linear(self) -> bool:
        return self.decoding is None

    @functools.cached_property
    def are_linear(self) -> bool:
        """
        Return True if the encoding and decoding are linear transfer-functions.
        """
        return self.is_encoding_linear and self.is_decoding_linear

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "is_encoding_linear": self.is_encoding_linear,
            "is_decoding_linear": self.is_decoding_linear,
        }

    @classmethod
    def from_colour_colorspace(
        cls, colour_colorspace: colour.RGB_Colourspace
    ) -> TransferFunctions:
        encoding = None
        decoding = None

        if colour_colorspace.cctf_encoding != colour.linear_function:
            encoding = colour_colorspace.cctf_encoding

        if colour_colorspace.cctf_decoding != colour.linear_function:
            decoding = colour_colorspace.cctf_decoding

        return cls(
            name="CCTF " + colour_colorspace.name,
            encoding=encoding,
            decoding=decoding,
        )


TRANSFER_FUNCTIONS_LINEAR = TransferFunctions("CCTF Linear", None, None)


@dataclasses.dataclass(eq=False, frozen=True)
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

    categories: tuple[ColorspaceCategory, ...]
    """
    To help sort the colorspace in an interface.
    """

    description: str
    """
    A bit more details on what/why for this colorspace.
    """

    matrix_to_XYZ: Optional[numpy.ndarray]
    matrix_from_XYZ: Optional[numpy.ndarray]

    _linear_source: Optional[RgbColorspace] = None
    """
    Initial colorspace this instance was derived from when linearized.
    """

    _matrix_to_XYZ_derived: bool = False
    _matrix_from_XYZ_derived: bool = False

    @functools.cached_property
    def _tuplerepr(self) -> tuple:
        return (
            self.__class__.__name__,
            self.name,
            self.gamut,
            self.whitepoint,
            self.transfer_functions,
            self.categories,
            self.description,
            repr(self.matrix_to_XYZ),
            repr(self.matrix_from_XYZ),
        )

    @functools.cached_property
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
        new_colorspace = self.copy()

        if not self.transfer_functions or self.transfer_functions.are_linear:
            return new_colorspace

        # noinspection PyTypeChecker
        return RgbColorspace(
            name=new_colorspace.name + " Linear",
            description=new_colorspace.description,
            gamut=new_colorspace.gamut,
            whitepoint=new_colorspace.whitepoint,
            transfer_functions=TRANSFER_FUNCTIONS_LINEAR,
            categories=new_colorspace.categories,
            matrix_to_XYZ=new_colorspace.matrix_to_XYZ,
            matrix_from_XYZ=new_colorspace.matrix_from_XYZ,
            _linear_source=self,
        )

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

    def with_derived_matrices(self) -> RgbColorspace:
        """
        Return a copy of this instance but the XYZ conversion matrices derived
        from the gamut and whitepoint.

        Note that they might still be None if gamut and whitepoint are not defined.
        """
        if not self.gamut or not self.whitepoint:
            return self.with_gamut(self.gamut, None, None)

        matrix_to_XYZ = self.compute_matrix_to_XYZ_from(self.gamut, self.whitepoint)
        matrix_from_XYZ = self.compute_matrix_from_XYZ_from(self.gamut, self.whitepoint)
        new_colorspace = self.copy()

        return RgbColorspace(
            name=new_colorspace.name,
            gamut=new_colorspace.gamut,
            whitepoint=new_colorspace.whitepoint,
            transfer_functions=new_colorspace.transfer_functions,
            categories=new_colorspace.categories,
            description=new_colorspace.description,
            matrix_to_XYZ=matrix_to_XYZ,
            matrix_from_XYZ=matrix_from_XYZ,
            _linear_source=new_colorspace._linear_source,
            _matrix_to_XYZ_derived=True,
            _matrix_from_XYZ_derived=True,
        )

    def with_descriptives(
        self,
        new_name: Optional[str] = None,
        new_description: Optional[str] = None,
        new_categories: Optional[tuple[ColorspaceCategory, ...]] = None,
    ) -> RgbColorspace:
        """
        Return this instance with the given "descriptive" attribute modified.

        If the attribute is None, use the current one on this instance.

        Args:
            new_name: None to use the current instance one
            new_description: None to use the current instance one
            new_categories: None to use the current instance one

        Returns:
            new instance
        """
        new_colorspace = self.copy()
        new_name = new_name or new_colorspace.name
        new_description = new_description or new_colorspace.description
        new_categories = (
            new_categories if new_categories is not None else new_colorspace.categories
        )
        return RgbColorspace(
            name=new_name,
            categories=new_categories,
            description=new_description,
            gamut=new_colorspace.gamut,
            whitepoint=new_colorspace.whitepoint,
            transfer_functions=new_colorspace.transfer_functions,
            matrix_to_XYZ=new_colorspace.matrix_to_XYZ,
            matrix_from_XYZ=new_colorspace.matrix_from_XYZ,
            _linear_source=new_colorspace._linear_source,
        )

    def with_gamut(
        self,
        new_gamut: Optional[ColorspaceGamut],
        matrix_to_XYZ: Optional[numpy.ndarray],
        matrix_from_XYZ: Optional[numpy.ndarray],
    ) -> RgbColorspace:
        """
        Return a copy of this instance with the given gamut set.

        Changing the gamut means teh matrices need to be provided again.
        Tip: You can just pass None for matrices and call :meth:`with_derived_matrices`
        after.

        Args:
            new_gamut:
            matrix_to_XYZ:
            matrix_from_XYZ:

        Returns:
            new object
        """
        new_colorspace = self.copy()
        return RgbColorspace(
            name=new_colorspace.name,
            gamut=new_gamut,
            whitepoint=new_colorspace.whitepoint,
            transfer_functions=new_colorspace.transfer_functions,
            categories=new_colorspace.categories,
            description=new_colorspace.description,
            matrix_to_XYZ=matrix_to_XYZ,
            matrix_from_XYZ=matrix_from_XYZ,
            _linear_source=new_colorspace._linear_source,
        )

    def with_transfer_functions(
        self,
        new_transfer_functions: Optional[TransferFunctions],
    ) -> RgbColorspace:
        """
        Return a copy of this instance with the given whitepoint set.

        Args:
            new_transfer_functions:

        Returns:
            new object
        """
        new_colorspace = self.copy()
        return RgbColorspace(
            name=new_colorspace.name,
            gamut=new_colorspace.gamut,
            whitepoint=new_colorspace.whitepoint,
            transfer_functions=new_transfer_functions,
            categories=new_colorspace.categories,
            description=new_colorspace.description,
            matrix_to_XYZ=new_colorspace.matrix_to_XYZ,
            matrix_from_XYZ=new_colorspace.matrix_from_XYZ,
            _linear_source=new_colorspace._linear_source,
        )

    def with_whitepoint(
        self,
        new_whitepoint: Optional[Whitepoint],
        matrix_to_XYZ: Optional[numpy.ndarray],
        matrix_from_XYZ: Optional[numpy.ndarray],
    ) -> RgbColorspace:
        """
        Return a copy of this instance with the given whitepoint set.

        Args:
            new_whitepoint:
            matrix_to_XYZ:
            matrix_from_XYZ:

        Returns:
            new object
        """
        new_colorspace = self.copy()
        return RgbColorspace(
            name=new_colorspace.name,
            gamut=new_colorspace.gamut,
            whitepoint=new_whitepoint,
            transfer_functions=new_colorspace.transfer_functions,
            categories=new_colorspace.categories,
            description=new_colorspace.description,
            matrix_to_XYZ=matrix_to_XYZ,
            matrix_from_XYZ=matrix_from_XYZ,
            _linear_source=new_colorspace._linear_source,
        )

    @classmethod
    def compute_matrix_to_XYZ_from(cls, gamut, whitepoint) -> numpy.ndarray:
        """
        Compute the normalized primary matrix from the given gamut and whitepoint, to XYZ.

        Args:
            gamut:
            whitepoint:

        Returns:
            3x3 matrix
        """
        return colour.normalised_primary_matrix(
            primaries=gamut.primaries,
            whitepoint=whitepoint.coordinates,
        )

    @classmethod
    def compute_matrix_from_XYZ_from(cls, gamut, whitepoint) -> numpy.ndarray:
        """
        Compute the normalized primary matrix from the given gamut and whitepoint, from XYZ.

        Args:
            gamut:
            whitepoint:

        Returns:
            3x3 matrix
        """
        return numpy.linalg.inv(cls.compute_matrix_to_XYZ_from(gamut, whitepoint))

    @classmethod
    def from_colour_colorspace(
        cls,
        colour_colorspace: colour.RGB_Colourspace,
        categories: list[ColorspaceCategory],
        description: Optional[str] = None,
    ) -> RgbColorspace:
        gamut = ColorspaceGamut.from_colour_colorspace(colour_colorspace)
        whitepoint = Whitepoint.from_colour_colorspace(colour_colorspace)
        transfer_functions = TransferFunctions.from_colour_colorspace(colour_colorspace)

        return cls(
            name=colour_colorspace.name,
            gamut=gamut,
            whitepoint=whitepoint,
            transfer_functions=transfer_functions,
            description=description or colour_colorspace.__doc__,
            categories=tuple(categories),
            matrix_from_XYZ=colour_colorspace.matrix_XYZ_to_RGB.copy(),
            matrix_to_XYZ=colour_colorspace.matrix_RGB_to_XYZ.copy(),
            _matrix_to_XYZ_derived=colour_colorspace.use_derived_matrix_RGB_to_XYZ,
            _matrix_from_XYZ_derived=colour_colorspace.use_derived_matrix_XYZ_to_RGB,
        )
