import importlib
import logging

import colour

import cocoon.cfg
from cocoon.colorspaces import RgbColorspace
from cocoon.colorspaces import Whitepoint
from cocoon.colorspaces import ColorspaceCategory

logger = logging.getLogger(__name__)

_COLORSPACES: dict[str, RgbColorspace] = {}
"""
Data dict of all the colorspaces available in the package. The key represent an identifier
to access the corresponding colorspace.

You can have multiple keys poiting to the same colorspace instance. 
This allow to created "alias" identifiers.

TODO determine if the dict is sorted
"""

# Names of special colorspace that must be handled differently
_COLORSPACE_POINTER_GAMUT_NAME = "Pointer's Gamut"


def _add_colorspace(colorspace: RgbColorspace, additional_aliases: list[str] = None):
    """
    Register the given colorspace in the package.

    Args:
        colorspace: colorspace class instance
        additional_aliases: optional list of str that can return the colorspace when queried.
    """

    global _COLORSPACES
    additional_aliases = additional_aliases or []

    _COLORSPACES[colorspace.name] = colorspace
    _COLORSPACES[colorspace.name_simplified] = colorspace

    for alias in additional_aliases:
        _COLORSPACES[alias] = colorspace

    return


def _patch_colour_colorspace(
    colorspace: colour.RGB_Colourspace,
) -> colour.RGB_Colourspace:
    """
    Override attributes on some specific colour colorspaces.

    Args:
        colorspace: colour colorspace to patch.

    Returns:
        patched colorspace instance or original if no patch applied.
    """
    if cocoon.cfg.colorspaces_use_derived_transformation_matrices:
        colorspace.use_derived_transformation_matrices(True)

    if colorspace.name == "sRGB":
        colorspace.name = "sRGB Piecewise"

    return colorspace


def _load_colour_colorspaces():
    """
    Use the colour library as the main dataset for colorspaces and load them in this
    library.
    """
    colour_colorspace_config = {
        "RGB_COLOURSPACE_ACES2065_1": {
            "category": [ColorspaceCategory.aces],
            "aliases": ["aces", "ap0"],
        },
        "RGB_COLOURSPACE_ACESCC": {
            "category": [ColorspaceCategory.aces],
        },
        "RGB_COLOURSPACE_ACESCCT": {
            "category": [ColorspaceCategory.aces],
        },
        "RGB_COLOURSPACE_ACESPROXY": {
            "category": [ColorspaceCategory.aces],
        },
        "RGB_COLOURSPACE_ACESCG": {
            "category": [ColorspaceCategory.aces, ColorspaceCategory.working_space],
            "aliases": ["ap1"],
        },
        "RGB_COLOURSPACE_ADOBE_RGB1998": {
            "category": [ColorspaceCategory.common],
        },
        "RGB_COLOURSPACE_ADOBE_WIDE_GAMUT_RGB": {
            "category": [ColorspaceCategory.working_space],
        },
        "RGB_COLOURSPACE_ARRI_WIDE_GAMUT_4": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_ARRI_WIDE_GAMUT_3": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_APPLE_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_BEST_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_BETA_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_BLACKMAGIC_WIDE_GAMUT": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_BT470_525": {
            "category": [],
        },
        "RGB_COLOURSPACE_BT470_625": {
            "category": [],
        },
        "RGB_COLOURSPACE_BT709": {
            "category": [ColorspaceCategory.common],
            "aliases": ["rec709", "bt709"],
        },
        "RGB_COLOURSPACE_BT2020": {
            "category": [ColorspaceCategory.working_space],
            "aliases": ["rec2020", "bt2020"],
        },
        "RGB_COLOURSPACE_CIE_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_CINEMA_GAMUT": {
            "category": [],
        },
        "RGB_COLOURSPACE_COLOR_MATCH_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_DAVINCI_WIDE_GAMUT": {
            "category": [ColorspaceCategory.working_space],
        },
        "RGB_COLOURSPACE_DCDM_XYZ": {
            "category": [],
        },
        "RGB_COLOURSPACE_DCI_P3": {
            "category": [ColorspaceCategory.p3],
        },
        "RGB_COLOURSPACE_DCI_P3_P": {
            "category": [ColorspaceCategory.p3],
        },
        "RGB_COLOURSPACE_DISPLAY_P3": {
            "category": [ColorspaceCategory.p3],
        },
        "RGB_COLOURSPACE_DJI_D_GAMUT": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_DON_RGB_4": {
            "category": [],
        },
        "RGB_COLOURSPACE_ECI_RGB_V2": {
            "category": [],
        },
        "RGB_COLOURSPACE_EKTA_SPACE_PS_5": {
            "category": [],
        },
        "RGB_COLOURSPACE_FILMLIGHT_E_GAMUT": {
            "category": [ColorspaceCategory.working_space],
        },
        "RGB_COLOURSPACE_PROTUNE_NATIVE": {
            "category": [],
        },
        "RGB_COLOURSPACE_MAX_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_N_GAMUT": {
            "category": [],
        },
        "RGB_COLOURSPACE_P3_D65": {
            "category": [ColorspaceCategory.p3],
        },
        "RGB_COLOURSPACE_PAL_SECAM": {
            "category": [],
        },
        "RGB_COLOURSPACE_RED_COLOR": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_RED_COLOR_2": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_RED_COLOR_3": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_RED_COLOR_4": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_DRAGON_COLOR": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_DRAGON_COLOR_2": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_RED_WIDE_GAMUT_RGB": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_ROMM_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_RIMM_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_ERIMM_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_PROPHOTO_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_RUSSELL_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_SHARP_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_SMPTE_240M": {
            "category": [],
        },
        "RGB_COLOURSPACE_SMPTE_C": {
            "category": [],
        },
        "RGB_COLOURSPACE_NTSC1953": {
            "category": [],
        },
        "RGB_COLOURSPACE_NTSC1987": {
            "category": [],
        },
        "RGB_COLOURSPACE_S_GAMUT": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_S_GAMUT3": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_S_GAMUT3_CINE": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_VENICE_S_GAMUT3": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_VENICE_S_GAMUT3_CINE": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_sRGB": {
            "category": [ColorspaceCategory.working_space, ColorspaceCategory.common],
            "aliases": ["srgb", "sRGB"],
        },
        "RGB_COLOURSPACE_V_GAMUT": {
            "category": [ColorspaceCategory.camera],
        },
        "RGB_COLOURSPACE_XTREME_RGB": {
            "category": [],
        },
        "RGB_COLOURSPACE_F_GAMUT": {
            "category": [ColorspaceCategory.camera],
        },
    }

    colour_dataset = importlib.import_module("colour.models.rgb.datasets")

    for colorspace_name, colorspace_data in colour_colorspace_config.items():
        try:
            colour_colorspace: colour.RGB_Colourspace = getattr(
                colour_dataset, colorspace_name
            )
        except ImportError as excp:
            logger.error(
                f"[_load_colour_colorspaces] Colour colorspace <{colorspace_name} was not imported: {excp}>"
            )
            continue

        colour_colorspace = colour_colorspace.copy()
        colour_colorspace_patched = _patch_colour_colorspace(colour_colorspace)

        colorspace = RgbColorspace.from_colour_colorspace(
            colour_colorspace_patched,
            categories=colorspace_data.get("category", []),
        )

        aliases = colorspace_data.get("aliases", [])
        _add_colorspace(colorspace, additional_aliases=aliases)

    return


def _load_colorspaces():
    """
    Create the colorspace dataset.

    Intended to be called once.
    """

    _load_colour_colorspaces()

    colorspace = RgbColorspace(
        name="Passthrough",
        gamut=None,
        whitepoint=None,
        transfer_functions=None,
        description="A 'null' colorspace that does nothing.",
        categories=(ColorspaceCategory.common, ColorspaceCategory.special),
        matrix_from_XYZ=None,
        matrix_to_XYZ=None,
    )
    _add_colorspace(colorspace, additional_aliases=["raw", "null"])

    whitepoint = Whitepoint(
        f"{_COLORSPACE_POINTER_GAMUT_NAME} Whitepoint",
        coordinates=colour.models.CCS_ILLUMINANT_POINTER_GAMUT,
    )
    colorspace = RgbColorspace(
        name=_COLORSPACE_POINTER_GAMUT_NAME,
        gamut=None,
        whitepoint=whitepoint,
        transfer_functions=None,
        description=(
            "The Pointer’s gamut is (an approximation of) the gamut of real surface "
            "colors as can be seen by the human eye, based on the research by "
            "Michael R. Pointer (1980). What this means is that every color that can "
            "be reflected by the surface of an object of any material is inside the "
            "Pointer’s gamut.\n Pointer’s gamut is defined for diffuse reflection "
            "(matte surface). "
            "Specular reflection objects can reflect colors that are outside the Pointer’s gamut. \n"
            "Also not technically a colorspace."
        ),
        categories=(ColorspaceCategory.special,),
        matrix_from_XYZ=None,
        matrix_to_XYZ=None,
    )
    _add_colorspace(colorspace)
