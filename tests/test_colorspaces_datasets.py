from cocoon import colorspaces
import cocoon.colorspaces.datasets.browse


def test_get_colorspace():
    result_a = colorspaces.get_colorspace("srgb")
    result_b = colorspaces.get_colorspace("sRGB")
    assert result_a
    assert result_b
    assert result_a is result_b

    result_a = colorspaces.get_colorspace("Adobe RGB (1998)")
    result_b = colorspaces.get_colorspace("adobe-rgb-1998")
    assert result_a
    assert result_b
    assert result_a is result_b

    result_a = colorspaces.get_colorspace("DCI-P3-P")
    result_b = colorspaces.get_colorspace("dci-p3-p")
    assert result_a
    assert result_b
    assert result_a is result_b

    return


def test_get_colorspace_linear():
    result = colorspaces.get_colorspace("srgb")
    assert result.transfer_functions != colorspaces.TRANSFER_FUNCTIONS_LINEAR

    result = colorspaces.get_colorspace("srgb", force_linear=True)
    assert result.transfer_functions == colorspaces.TRANSFER_FUNCTIONS_LINEAR

    result = colorspaces.get_colorspace("DCI-P3-P")
    assert result.transfer_functions != colorspaces.TRANSFER_FUNCTIONS_LINEAR

    result = colorspaces.get_colorspace("DCI-P3-P", force_linear=True)
    assert result.transfer_functions == colorspaces.TRANSFER_FUNCTIONS_LINEAR


def test_disable_colorspaces():
    colorspace_acescg = colorspaces.get_colorspace("ACEScg")
    assert colorspace_acescg is not None
    assert colorspace_acescg in colorspaces.get_available_colorspaces()
    assert colorspaces.get_colorspace("ap1") is colorspace_acescg
    assert colorspaces.get_colorspace("acescg") is colorspace_acescg
    assert colorspaces.get_colorspace("sRGB") is not None
    assert colorspaces.get_colorspace("Passthrough") is not None

    with cocoon.colorspaces.datasets.browse.disable_colorspaces(
        ["Passthrough", "ACEScg"]
    ):
        assert colorspaces.get_colorspace("ACEScg") is None
        assert colorspaces.get_colorspace("ap1") is None
        assert colorspaces.get_colorspace("acescg") is None
        assert colorspaces.get_colorspace("Passthrough") is None
        assert colorspaces.get_colorspace("raw") is None
        assert "ACEScg" not in colorspaces.get_available_colorspaces_names()

    assert colorspaces.get_colorspace("ACEScg") is not None
    assert colorspaces.get_colorspace("ap1") is not None
    assert colorspaces.get_colorspace("acescg") is not None
    assert colorspaces.get_colorspace("Passthrough") is not None

    with cocoon.colorspaces.datasets.browse.disable_colorspaces(
        ["Passthrough", "ACEScg"]
    ):
        with cocoon.colorspaces.datasets.browse.disable_colorspaces(["sRGB"]):
            assert colorspaces.get_colorspace("ACEScg") is None
            assert colorspaces.get_colorspace("sRGB") is None
            assert colorspaces.get_colorspace("Passthrough") is None

    assert colorspaces.get_colorspace("ACEScg") is not None
    assert colorspaces.get_colorspace("sRGB") is not None
    assert colorspaces.get_colorspace("Passthrough") is not None


def test__get_colorspace_aliases():
    colorspace = cocoon.sRGB_COLORSPACE
    result = cocoon.colorspaces.datasets.browse._get_colorspace_aliases(colorspace)
    expected = ["sRGB Piecewise", "srgb-piecewise", "srgb", "sRGB"]
    assert result == expected
