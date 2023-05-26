import colour
import numpy
import numpy.testing

from cocoon import colorspaces


def test_Whitepoint():
    # valid for now, see in the future
    whitepoint = colorspaces.Whitepoint("blank", coordinates=[])

    whitepoint_coord = colour.colorimetry.CCS_ILLUMINANTS[
        "CIE 1931 2 Degree Standard Observer"
    ]["D65"]
    whitepoint = colorspaces.Whitepoint("test d65", coordinates=whitepoint_coord)

    colorspace = colour.RGB_COLOURSPACES["sRGB"]

    whitepoint_srgb = colorspaces.Whitepoint.from_colour_colorspace(colorspace)
    assert numpy.array_equal(whitepoint_srgb.coordinates, whitepoint.coordinates)
    assert whitepoint_srgb.name == "D65"

    whitepoint_list = [
        colorspaces.Whitepoint("test d65", coordinates=whitepoint_coord),
        colorspaces.Whitepoint("test d65", coordinates=whitepoint_coord),
        colorspaces.Whitepoint("test d65", coordinates=whitepoint_coord * 2),
        colorspaces.Whitepoint("test d60", coordinates=whitepoint_coord),
    ]
    assert len(set(whitepoint_list)) == 3


def test_TransferFunctions():
    # valid for now, see in the future
    transfer_functions = colorspaces.TransferFunctions(
        "CCTF test",
        "",
        "",
    )

    transfer_functions = colorspaces.TransferFunctions(
        "CCTF test",
        encoding=lambda array: array**2,
        decoding=lambda array: array**1 / 2,
    )
    assert transfer_functions.are_linear is False
    assert transfer_functions.is_encoding_linear is False
    assert transfer_functions.is_decoding_linear is False

    transfer_functions = colorspaces.TransferFunctions(
        "CCTF test",
        encoding=lambda array: array**2,
        decoding=None,
    )
    assert transfer_functions.are_linear is False
    assert transfer_functions.is_encoding_linear is False
    assert transfer_functions.is_decoding_linear is True

    transfer_functions = colorspaces.TransferFunctions(
        "CCTF test",
        encoding=None,
        decoding=None,
    )
    assert transfer_functions.are_linear is True
    assert transfer_functions.is_encoding_linear is True
    assert transfer_functions.is_decoding_linear is True

    transfer_functions_list = [
        colorspaces.TransferFunctions(
            "CCTF test",
            encoding=lambda array: array**2,
            decoding=lambda array: array**1 / 2,
        ),
        colorspaces.TransferFunctions(
            "CCTF test",
            encoding=lambda array: array**2,
            decoding=lambda array: array**1 / 2,
        ),
    ]
    assert len(set(transfer_functions_list)) == 2

    def temp_decoding_1(array):
        return array**2

    def temp_encoding_1(array):
        return array**1 / 2

    transfer_functions_list = [
        colorspaces.TransferFunctions(
            "CCTF test",
            encoding=temp_encoding_1,
            decoding=temp_decoding_1,
        ),
        colorspaces.TransferFunctions(
            "CCTF test",
            encoding=temp_encoding_1,
            decoding=temp_decoding_1,
        ),
    ]
    assert len(set(transfer_functions_list)) == 1

    transfer_functions_list = [
        colorspaces.TransferFunctions(
            "CCTF test",
            encoding=None,
            decoding=temp_decoding_1,
        ),
        colorspaces.TransferFunctions(
            "CCTF test",
            encoding=temp_encoding_1,
            decoding=temp_decoding_1,
        ),
    ]
    assert len(set(transfer_functions_list)) == 2


def test_RgbColorspace_fromColour():
    colour_colorspace: colour.RGB_Colourspace = colour.RGB_COLOURSPACES["sRGB"]

    colorspace = colorspaces.RgbColorspace.from_colour_colorspace(
        colour_colorspace,
        categories=[colorspaces.ColorspaceCategory.common],
    )

    assert colorspace.name == "sRGB Piecewise"
    assert colorspace.categories == (colorspaces.ColorspaceCategory.common,)
    assert colorspace.description == colour_colorspace.__doc__
    numpy.testing.assert_array_equal(
        colorspace.matrix_to_XYZ,
        colour_colorspace.matrix_RGB_to_XYZ,
    )
    numpy.testing.assert_array_equal(
        colorspace.matrix_from_XYZ,
        colour_colorspace.matrix_XYZ_to_RGB,
    )
    assert colorspace.matrix_from_XYZ is not colour_colorspace.matrix_XYZ_to_RGB

    numpy.testing.assert_array_equal(
        colorspace.whitepoint.coordinates,
        colour_colorspace.whitepoint,
    )
    assert colorspace.whitepoint.coordinates is not colour_colorspace.whitepoint

    colorspace = colorspaces.RgbColorspace.from_colour_colorspace(
        colour_colorspace,
        categories=tuple(),
        description="test description",
    )
    assert colorspace.description == "test description"


def test_RgbColorspace_is_no_op():
    try:
        colorspace = colorspaces.RgbColorspace("test fail")
    except TypeError:
        pass
    else:
        raise AssertionError("Exception not raised.")

    colorspace = colorspaces.RgbColorspace(
        "test null", None, None, None, tuple(), "", None, None
    )
    assert colorspace.is_no_op is True

    # some test data

    def temp_decoding_1(array):
        return array**2

    def temp_encoding_1(array):
        return array**1 / 2

    transfer_functions = colorspaces.TransferFunctions(
        "CCTF test",
        encoding=temp_encoding_1,
        decoding=temp_decoding_1,
    )

    gamut_1 = colorspaces.ColorspaceGamut(
        "gamut 1",
        numpy.array([[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]]),
    )

    whitepoint = colorspaces.Whitepoint(
        "test illuminant",
        numpy.array([1 / 3, 1 / 3, 1 / 3]),
    )

    colorspace = colorspaces.RgbColorspace(
        "test null", None, None, None, tuple(), "", None, None
    )
    assert colorspace.is_no_op is True

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=None,
        whitepoint=None,
        transfer_functions=None,
        categories=tuple(),
        description="",
        matrix_from_XYZ=None,
        matrix_to_XYZ=None,
    )
    assert colorspace.is_no_op is True

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=gamut_1,
        whitepoint=None,
        transfer_functions=None,
        categories=tuple(),
        description="",
        matrix_from_XYZ=None,
        matrix_to_XYZ=None,
    )
    assert colorspace.is_no_op is False

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=None,
        whitepoint=whitepoint,
        transfer_functions=None,
        categories=tuple(),
        description="",
        matrix_from_XYZ=None,
        matrix_to_XYZ=None,
    )
    assert colorspace.is_no_op is False

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=None,
        whitepoint=None,
        transfer_functions=transfer_functions,
        categories=tuple(),
        description="",
        matrix_from_XYZ=None,
        matrix_to_XYZ=None,
    )
    assert colorspace.is_no_op is False

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=None,
        whitepoint=None,
        transfer_functions=None,
        categories=tuple(),
        description="",
        matrix_from_XYZ=numpy.identity(3),
        matrix_to_XYZ=numpy.identity(3),
    )
    assert colorspace.is_no_op is True

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=None,
        whitepoint=None,
        transfer_functions=None,
        categories=tuple(),
        description="",
        matrix_from_XYZ=numpy.identity(3) + 0.5,
        matrix_to_XYZ=numpy.identity(3) + 0.5,
    )
    assert colorspace.is_no_op is False


def test_RgbColorspace_matrices():
    def temp_decoding_1(array):
        return array**2

    def temp_encoding_1(array):
        return array**1 / 2

    transfer_functions = colorspaces.TransferFunctions(
        "CCTF test",
        encoding=temp_encoding_1,
        decoding=temp_decoding_1,
    )

    gamut_1 = colorspaces.ColorspaceGamut(
        "gamut 1",
        numpy.array([[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]]),
    )

    whitepoint = colorspaces.Whitepoint(
        "test illuminant",
        numpy.array([1 / 3, 1 / 3, 1 / 3]),
    )

    matrix_to = numpy.array(
        [[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]
    )

    matrix_from = numpy.array(
        [[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]
    )

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=gamut_1,
        whitepoint=whitepoint,
        transfer_functions=transfer_functions,
        categories=tuple(),
        description="",
        matrix_to_XYZ=None,
        matrix_from_XYZ=None,
    )
    assert colorspace.matrix_to_XYZ is None
    assert colorspace.matrix_from_XYZ is None

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=gamut_1,
        whitepoint=whitepoint,
        transfer_functions=transfer_functions,
        categories=tuple(),
        description="",
        matrix_to_XYZ=matrix_to,
        matrix_from_XYZ=matrix_from,
    )
    assert colorspace.matrix_to_XYZ is matrix_to
    assert colorspace.matrix_from_XYZ is matrix_from


def test_RgbColorspace_copy():
    def temp_decoding_1(array):
        return array**2

    def temp_encoding_1(array):
        return array**1 / 2

    transfer_functions = colorspaces.TransferFunctions(
        "CCTF test",
        encoding=temp_encoding_1,
        decoding=temp_decoding_1,
    )

    gamut_1 = colorspaces.ColorspaceGamut(
        "gamut 1",
        numpy.array([[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]]),
    )

    whitepoint = colorspaces.Whitepoint(
        "test illuminant",
        numpy.array([1 / 3, 1 / 3, 1 / 3]),
    )
    matrix_to = colorspaces.RgbColorspace.compute_matrix_to_XYZ_from(
        gamut_1, whitepoint
    )
    matrix_from = colorspaces.RgbColorspace.compute_matrix_from_XYZ_from(
        gamut_1, whitepoint
    )

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=gamut_1,
        whitepoint=whitepoint,
        transfer_functions=transfer_functions,
        categories=tuple(),
        description="",
        matrix_to_XYZ=matrix_to,
        matrix_from_XYZ=matrix_from,
    )

    colorspace_copy = colorspace.copy()
    assert colorspace_copy is not colorspace
    assert colorspace == colorspace_copy
    assert colorspace.gamut.primaries is not colorspace_copy.gamut.primaries
    assert (
        colorspace.whitepoint.coordinates is not colorspace_copy.whitepoint.coordinates
    )
    numpy.testing.assert_array_equal(
        colorspace.whitepoint.coordinates, colorspace_copy.whitepoint.coordinates
    )
    assert (
        colorspace.transfer_functions.decoding
        is colorspace_copy.transfer_functions.decoding
    )
    assert (
        colorspace.transfer_functions.encoding
        is colorspace_copy.transfer_functions.encoding
    )
    assert colorspace_copy.matrix_to_XYZ is not matrix_to
    assert colorspace_copy.matrix_from_XYZ is not matrix_from


def test_RgbColorspace_hashing():
    def temp_decoding_1(array):
        return array**2

    def temp_encoding_1(array):
        return array**1 / 2

    transfer_functions = colorspaces.TransferFunctions(
        "CCTF test",
        encoding=temp_encoding_1,
        decoding=temp_decoding_1,
    )

    gamut_1 = colorspaces.ColorspaceGamut(
        "gamut 1",
        numpy.array([[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]]),
    )

    whitepoint = colorspaces.Whitepoint(
        "test illuminant",
        numpy.array([1 / 3, 1 / 3, 1 / 3]),
    )
    matrix_to = colorspaces.RgbColorspace.compute_matrix_to_XYZ_from(
        gamut_1, whitepoint
    )
    matrix_from = colorspaces.RgbColorspace.compute_matrix_from_XYZ_from(
        gamut_1, whitepoint
    )

    colorspace_list = [
        colorspaces.RgbColorspace(
            "test A",
            gamut=gamut_1,
            whitepoint=whitepoint,
            transfer_functions=transfer_functions,
            categories=tuple(),
            description="",
            matrix_to_XYZ=matrix_to,
            matrix_from_XYZ=matrix_from,
        ),
        colorspaces.RgbColorspace(
            "test A",
            gamut=gamut_1,
            whitepoint=whitepoint,
            transfer_functions=transfer_functions,
            categories=tuple(),
            description="",
            matrix_to_XYZ=matrix_to,
            matrix_from_XYZ=matrix_from,
        ),
    ]
    assert len(set(colorspace_list)) == 1

    colorspace_list = [
        colorspaces.RgbColorspace(
            "test A",
            gamut=gamut_1,
            whitepoint=whitepoint,
            transfer_functions=transfer_functions,
            categories=tuple(),
            description="",
            matrix_to_XYZ=matrix_to,
            matrix_from_XYZ=matrix_from,
        ),
        colorspaces.RgbColorspace(
            "test B",
            gamut=gamut_1,
            whitepoint=whitepoint,
            transfer_functions=transfer_functions,
            categories=tuple(),
            description="",
            matrix_to_XYZ=matrix_to,
            matrix_from_XYZ=matrix_from,
        ),
    ]
    assert len(set(colorspace_list)) == 2

    colorspace_list = [
        colorspaces.RgbColorspace(
            "test A",
            gamut=gamut_1,
            whitepoint=whitepoint,
            transfer_functions=transfer_functions,
            categories=tuple(),
            description="",
            matrix_to_XYZ=matrix_to,
            matrix_from_XYZ=matrix_from,
        ),
        colorspaces.RgbColorspace(
            "test A",
            gamut=gamut_1,
            whitepoint=whitepoint,
            transfer_functions=transfer_functions,
            categories=tuple(),
            description="test",
            matrix_to_XYZ=matrix_to,
            matrix_from_XYZ=matrix_from,
        ),
    ]
    assert len(set(colorspace_list)) == 2


def test_RgbColorspace_get_linear_copy():
    def temp_decoding_1(array):
        return array**2

    def temp_encoding_1(array):
        return array**1 / 2

    transfer_functions = colorspaces.TransferFunctions(
        "CCTF test",
        encoding=temp_encoding_1,
        decoding=temp_decoding_1,
    )

    gamut_1 = colorspaces.ColorspaceGamut(
        "gamut 1",
        numpy.array([[0.64, 0.33], [0.3, 0.6], [0.15, 0.06]]),
    )

    whitepoint = colorspaces.Whitepoint(
        "test illuminant",
        numpy.array([1 / 3, 1 / 3, 1 / 3]),
    )

    matrix_to = colorspaces.RgbColorspace.compute_matrix_to_XYZ_from(
        gamut_1, whitepoint
    )
    matrix_from = colorspaces.RgbColorspace.compute_matrix_from_XYZ_from(
        gamut_1, whitepoint
    )

    colorspace = colorspaces.RgbColorspace(
        "test null",
        gamut=gamut_1,
        whitepoint=whitepoint,
        transfer_functions=transfer_functions,
        categories=tuple(),
        description="",
        matrix_to_XYZ=matrix_to,
        matrix_from_XYZ=matrix_from,
    )

    assert colorspace.is_linear_copy is False
    assert colorspace.transfer_functions.are_linear is False

    linear_colorspace = colorspace.as_linear_copy()
    assert linear_colorspace.is_linear_copy is True
    assert linear_colorspace.transfer_functions.are_linear is True
    assert linear_colorspace.retrieve_linear_source() is colorspace

    linear_colorspace_2 = linear_colorspace.as_linear_copy()
    assert linear_colorspace_2 is not linear_colorspace
    assert linear_colorspace_2.is_linear_copy is True
    assert linear_colorspace_2.transfer_functions.are_linear is True
    assert linear_colorspace_2.retrieve_linear_source() == colorspace
    # we made a deepcopy
    assert linear_colorspace_2.retrieve_linear_source() is not colorspace
